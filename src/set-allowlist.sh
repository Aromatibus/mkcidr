#!/bin/bash

# ルールをクリア
iptables -F

# デフォルトのポリシーを設定
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT

IP-LIST "=" "/var/ip-lists/ipv4/_CIDR.ipv4"

# Allowlistのセットを作成
ipset create -exist allow_list hash:net

# Allowlistのセットに日本のIPアドレスを登録
sed -n "s/^JP\t//p" "${IP-LIST}" | while read -r ADDRESS; do
    ipset add allow_list "${ADDRESS}"
done
