workflow "Check Home Assistant Configuration" {
  on = "push"
  resolves = ["STABLE", "RC"]
}

action "STABLE" {
  uses = "ludeeus/action-ha-config-check@master"
  env = {
    ACTION_VERSION = "STABLE"
  }
}

action "RC" {
  uses = "ludeeus/action-ha-config-check@master"
  env = {
    ACTION_VERSION = "RC"
  }
}
