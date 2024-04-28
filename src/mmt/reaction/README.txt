# Configuration of Reaction

- when an alert is shown in Web GUI, there will be 2 buttons, "Block Attack" and "Unblock", beside the alert
- the corresponding script will be executed
  + "Block Attack" button ==> the script "/opt/mmt/operator/data/attack/script/block-traffic.sh"
  + "Unblock" button ==> the script "/opt/mmt/operator/data/attack/script/unblock-traffic.sh"
- Note: the scripts must have the *execution* permission.

