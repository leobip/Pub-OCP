FROM alpine:3.16.1

LABEL maintainer="Delivery Engineering Team"
LABEL building_block="automation-toolbox"
LABEL version="1.0.0"

RUN apk update &&       \
apk add --no-cache curl jq bash git coreutils zip &&  \
rm -rf /var/cache/apk/*

RUN adduser -h /home/branchscan -g 1000 -u 1000 -s /bin/sh -D branchscan

WORKDIR /home/branchscan

ADD scan-bitbucket-branches.sh /home/branchscan/
RUN chmod +x /home/branchscan/scan-bitbucket-branches.sh

USER branchscan

ENTRYPOINT [ "/home/branchscan/scan-bitbucket-branches.sh" ]