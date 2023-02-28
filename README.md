# Description

This project extracts data from Fitbit's API (activity & sleep) and analyses it. 

The primary component is a daily batch processing pipeline that authenticates and pulls user data from the fitbit API, before creating an analytics-ready data set in AWS. Example dashboards are shown below but creating the visualisation layer is not part of this repository and is instead left to the user.

# Architecture

The technologies used in the project are listed below. 

<p align="center">
  <img src="https://github.com/cjbraley/fitbit_pipeline/raw/master/demo/architecture.png?raw=true" />
</p>


#### Infrastructure

The project uses GCP as cloud provider. Cloud infrastructure is managed as code using Terraform.

-   Docker
-   AWS
-   Terraform

#### Pipeline

The pipeline runs on a daily basis and is orchestrated by Prefect. The pipeline runs locally rather than in Docker because the current authentication process requires a browser to be opened.

-   Prefect
-   Amazon S3
-   Amazon Redshift
-   DBT

1. A valid authentication token for the Fitbit API is obtained
2. Data is requested from the Fitbit API
3. Data is written as parquet files to a buffer
4. Data is uploaded to S3
5. Data is copied to Redshift
6. DBT runs on Redshift and creates final tables used for analytics

#### Visualisation & Analysis

The visualisation, done in Tableau, is indicative and not part of this repository.

-   Looker Studo

# Dashboard

To give an indication of the type of analysis that can be done with the data, a sample dashboard was created in Tableau. The dashboard is not part of this repository.

**Analysis of Active Zones**


<p align="center">
  <img src="https://github.com/cjbraley/fitbit_pipeline/raw/master/demo/activity.png?raw=true" />
</p>

**Analysis of Sleep Quality**


<p align="center">
  <img src="https://github.com/cjbraley/fitbit_pipeline/raw/master/demo/sleep.png?raw=true" />
</p>

## Setup

**Requirements:**

1. Docker
2. AWS account (all infrastructured can be covered by the free tier)
3. Fitbit Device & Developer Account

**Step-by-step setup instructions:**

1. Clone this repository
2. Install dependencies
   * run "make install"
3. Get Fitbit API Client Id and Client Secret
   * Create a Fitbit account - `https://dev.fitbit.com/login`
   * Register an application - `https://dev.fitbit.com/apps/new`
   * Set Redirect URL to `http://127.0.0.1:8080/`
   * Set OAuth 2.0 Application Type to Personal
   * Add your Client ID and Client Secret to the .env file
4. Create AWS access / secret key (user should be an admin or have approrpiate permissions)
   * Go to IAM
   * Make sure your AWS account has appropriate permissions, e.g. `AdministratorAccess`
   * Go to security credentials > create access key
5. Create .env file from .env-example and update values
   * Rename to .env
   * Update values except AWS_BUCKET_NAME & REDSHIFT_CLUSTER_HOST
6. Build AWS infrastructure with terraform
   * run "make infra-init"
   * Update AWS_BUCKET_NAME & REDSHIFT_CLUSTER_HOST in .env using Terradata output
7. Create Redshift tables
   * run "make redshift-init"
8. Start Prefect Orion
   * run "make prefect-start"
9. Deploy flow in Orion
   * in another terminal run "make prefect-deploy"
9. Start a prefect worker
   * in another terminal run "make prefect-worker"
9. Optional: backfill for past dates
   * Update the start/ end dates in the file prefect_backfill.py
   * run "make prefect-backfill"
9. Optional: Connect to BI Tool to Redshift and analyse data