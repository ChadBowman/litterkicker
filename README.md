# Litterkicker 😼

Tired of your Litter Robot 3 not detecting your cats? Do you just hate it when your expensive litter box doesn't cycle and fills up with pee and feces to the point it smells really bad? Are you tired of your supposedly automatic litter box becoming unclean to the point your little ones decide to pee elsewhere like on your clothes?

Well I am! Good thing we can automate our problems away.

This tool simply checks the last time the Litter Robot successfully cycled. If the last cycle was older than the configurable duration, it will cycle the box. Otherwise it just waits.

## Usage

### Deploy to AWS using [Terraform](https://www.terraform.io/)

The most automatic approach is to deploy litterkicker to AWS so it runs all the time. This has been made very easy using terraform. Don't worry, this uses the smallest EC2 instance_type (t2.nano), so it's cheap!

```bash
cd terraform
terraform init
terraform apply
```

You will be prompted for your whisker account username, password, your local ip address, and your vpc_id. Alternatively, you can store these in a file: `terraform/terraform.tfvars`.


terraform.tfvars (example)
```hcl
whisker_username = "yourusername"
whisker_passwork = "yourpassword"
local_ip "0.0.0.0" # just google "what is my IP"
vpc_id = "vpc-12345" # you can find this on your AWS console
aws_region = "us-west-2"
```

Once created, you can use the output instructions on how to connect to your instance using ssh. From the instance, checking the state of the container is easy:

```bash
sudo su -
docker ps
docker logs -f $(docker ps | grep 'chadbowman0/litterkicker' | grep -Eo '^\w+')
```

### Docker

If you prefer to not use AWS, you can run it easily on any machine with docker.

```bash
docker run -e WHISKER_USERNAME=yourusername -e WHISKER_PASSWORD=yourpassword chadbowman0/litterkicker:latest
```

### Local

Running it locally with python is possible assuming you are using Python 3.11 and [poetry](https://python-poetry.org/docs/).

```bash
export WHISKER_USERNAME=yourusername
export WHISKER_PASSWORD=yourpassword
python -m venv venv && source venv/bin/activate
pip install poetry
poetry install
poetry run python .
```
