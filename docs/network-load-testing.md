# Network Load Testing

This document describes our network load testing plan. These tests center around switch responsiveness, and focus on testing for:

* Race conditions
* Latency

## Setup

1. Multiple nodes and multiple switchports
2. Scripts to run commands

### Scripts

* Multiple OpenStack switchport configuration commands on same switchport
* Multiple OpenStack switch configuration commands on multiple switchports
