provider "aws" {
  region = var.aws_region 
}

variable "aws_region" {
  type = string
  default = "us-west-2"
}

variable "whisker_username" {
  description = "Username for Whisker account"
  type = string
}

variable "whisker_password" {
  description = "Password for Whisker account"
  type = string
  sensitive = true
}

variable "local_ip" {
  description = "The public IP of your computer"
  type = string
}

variable "vpc_id" {
  description = "Your AWS VPC id"
  type = string
}

resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
}

resource "local_file" "private_key_file" {
  content = tls_private_key.ssh_key.private_key_pem
  filename = "litterkicker_key.pem"
  file_permission = "400"
}

resource "aws_key_pair" "ssh_key_pair" {
  key_name = "litterkicker"
  public_key = tls_private_key.ssh_key.public_key_openssh
}

resource "aws_security_group" "litterkicker_sg" {
  name = "litterkicker-sg"
  vpc_id = var.vpc_id
}

resource "aws_security_group_rule" "ssh_ingress" {
  security_group_id = aws_security_group.litterkicker_sg.id
  type = "ingress"
  from_port = 22
  to_port = 22
  protocol = "tcp"
  cidr_blocks = ["${var.local_ip}/32"]
}

resource "aws_security_group_rule" "internet_egress" {
  security_group_id = aws_security_group.litterkicker_sg.id
  type = "egress"
  from_port = 0
  to_port = 65535
  protocol = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}

resource "aws_instance" "litterkicker" {
  ami = "ami-00970f57473724c10" # Amazon Linux 2023
  instance_type = "t2.nano"
  vpc_security_group_ids = [aws_security_group.litterkicker_sg.id]
  key_name = aws_key_pair.ssh_key_pair.key_name

  user_data = <<-EOF
    #!/bin/bash 
    sudo yum update
    sudo yum install -y docker
    sudo systemctl start docker
    sudo docker run -d \
      -e WHISKER_USERNAME=${var.whisker_username} \
      -e WHISKER_PASSWORD=${var.whisker_password} \
      chadbowman0/litterkicker:latest
  EOF
}

output "connect_instructions" {
  value = "ssh -i ${local_file.private_key_file.filename} ec2-user@${aws_instance.litterkicker.public_dns}"
}
