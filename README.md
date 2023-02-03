# Cloudflare & Namecheap API Script

This is a Python script for quickly performing various Cloudflare and Namecheap related tasks using the Cloudflare and Namecheap APIs.

## Usage

The script requires a `credentials.yaml` file with your Cloudflare and Namecheap API credentials. The file must contain a `CF_ACCOUNTS` list with your Cloudflare accounts, and `NC_API_USER` and `NC_API_KEY` with your Namecheap credentials.

Once your credentials are set up, run the script with `python cloudflare.py`. You will be presented with a list of Cloudflare accounts to choose from, and then a list of tasks you can perform.

## Tasks

Currently, the following tasks are supported:

* Add zone
* Enforce HTTPS
* Add record
* Add CNAME record
* Remove record
* Update nameservers of domain
