These [ansible](https://www.ansible.com/) configurations allow us to deploy / delete NEAMT servers on multiple hosts. Please change the files accordingly before running them.

To install ansible locally:
`sudo apt install ansible`

To delete all docker containers & images along with NEAMT data:
`ansible-playbook -K delete_all.yml`

To build and deploy NEAMT:
`ansible-playbook -K setup.yml`