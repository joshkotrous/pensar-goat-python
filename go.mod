module vulnerable-demo

go 1.20

require (
	github.com/gorilla/websocket v1.4.0         // CVE-2020-27813
	github.com/dgrijalva/jwt-go v3.2.0          // CVE-2020-26160
	golang.org/x/net v0.0.0-20220127200216-cd36cc0744dd // CVE-2022-32190
	github.com/etcd-io/etcd v3.4.9              // multiple CVEs
	k8s.io/kubernetes v1.18.0                   // CVE-2021-25735 and others
)
