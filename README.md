# Auto Lead Scoring
ALS has the goal of delivering the automotive industry's highest quality 3rd party leads
by purchasing only those leads which score well against the ALS scoring model. 

Backend is currently deployed on `Engine Yard EYK`. This repository contains the back-end for FSM workflow tool.
- **Project Board:** https://github.com/trilogy-group/ti-auto-lead-scoring-backend
- **Backend Url:** https://auto-lead-scoring.stage2.cnu-tu.ey.io/

## Deploying the AWS Resources
1) Install [AWS SAM](https://aws.amazon.com/serverless/sam/)
2) Ensure your AWS credentials are correctly configured
3) Set the `SAM_BUCKET_NAME` environment variable to specify the S3 bucket to use for SAM packaging
5) Run `make`

## Quick Start

```
From backend folder in project directory, run:
- pip3 install -r fast-api-als/requirements.txt
- uvicorn main:app --reload
```
## Test Api in Local
```
- send a POST request to localhost:8000\register3pl with a json body
 { username: "test-user" , password: "password" } to register a user and get an auth token
- use x-api-key header to send auth token 
- hit localhost:8000\submit to submit a lead
```

## Maintainers

Sahil Bajaj • [Github](https://github.com/sahil-ti)
Nitish Bharti • [Github](https://github.com/nitish-ti)

## Support

To raise an issue or feature requests visit https://github.com/trilogy-group/ti-auto-lead-scoring-backend/issues