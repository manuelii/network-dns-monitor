# Portfolio Notes

## GitHub repository description

Python network automation tool for device availability and DNS validation with
continuous monitoring, structured logs, email alerts, REST ticket creation,
tests, and GitHub Actions.

## Suggested GitHub topics

`python` `network-automation` `dns` `monitoring` `incident-response`
`devops` `sre` `cybersecurity` `rest-api` `smtp`

## Resume bullet

- Built a Python network and DNS monitoring application that validates device
  availability and expected IPv4 records, generates structured evidence,
  sends optional SMTP alerts, creates REST-based incident tickets, and runs
  automated tests through GitHub Actions.

## LinkedIn project description

Developed a Python network automation project that monitors device
availability and DNS records, classifies outages and DNS drift, records
timestamped evidence, sends email alerts, and creates incident tickets through
local or REST backends. Added a safe simulation mode, continuous monitoring,
environment-based secret handling, unit tests, and GitHub Actions CI.

## Interview talking points

- Why simulation mode makes the project easy and safe to evaluate
- How immutable data classes separate device configuration from check results
- Why JSON Lines works well for append-only incident records
- How environment variables keep tokens and passwords out of the repository
- How local and webhook backends make external integrations optional
- What would change for hundreds or thousands of devices

