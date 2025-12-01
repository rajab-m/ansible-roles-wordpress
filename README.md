# Ansible Role: WordPress

This Ansible role installs and configures a WordPress site on a target server. It sets up WordPress files, configures the database connection, and generates the `wp-config.php` file with secure keys. The role can be applied via a playbook to deploy WordPress quickly and consistently. Sensitive data such as passwords and credentials should be provided at runtime and not stored in the repository.

---

## Usage

Clone the repository and run your playbook to apply the role:

```
git clone https://github.com/rajab-m/ansible-roles-wordpress.git
cd ansible-roles-wordpress
ansible-playbook -i inventory.yaml install_wordpress.yaml
```
> **Note:** you have to modify the ips, DNS and credentials values found in these files:
> host_vars/db.yaml, host_vars/web.yaml, test_connection.py, roles/wordpress/defaults/main.yml, roles/MySql/defaults/main.yml, group_vars/all.yaml
