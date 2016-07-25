#!/bin/bash
ps fax | grep -Eo "php-fpm: pool $1[[:space:]]" | wc -l
