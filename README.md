# djanvaslms

A Django layer on top of Canvas LMS (Learning Management System)
- Uses the Canvas API to get information from Canvas into Django
- Goals:
  - scratch the itch: learn about Django by playing around with it
  - facilitate new educational apps
  - provide students of software engineering and data science a
    practical opportunity to get their hands dirty
  - use programming and devops as the primary LMS user interface
    rather than the standard Canvas web interface
  - make use of Canvas's open api, and incredibly valuable feature
  
## Current Status: *under development*

- install Postgresql
  - Postgres was chosen over other RDBMS backends because of it's jsonb
    column type, which makes loading json responses from the Canvas
    api extremely convenient
  - Other DB backends may be supported in the future
- install django, and other libraries
  - ```pip install -r requirements.txt```
  - virtualenvironments are a good idea
- get Canvas api token
  - (under Account -> Settings -> Approved Integrations -> New Access Token)
  - eventually this will use full OAUTH but currently the token is
    just saved in an environment variable ($DJANVAS_TOKEN)
