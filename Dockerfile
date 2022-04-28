FROM ghcr.io/gigahawk/freecad-cli:0.19.4_2

COPY entrypoint.sh /
COPY export.py /

ENTRYPOINT ["/entrypoint.sh"]