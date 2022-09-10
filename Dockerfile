FROM ghcr.io/gigahawk/freecad-cli:0.19.4_2

RUN \
    add-apt-repository --yes ppa:kicad/kicad-6.0-releases \
    && apt update \
    && apt install -y --install-recommends kicad

RUN \
    cd /usr/local/Mod/ \
    && git clone https://github.com/easyw/kicadStepUpMod.git

COPY entrypoint.sh /
COPY export.py /

ENTRYPOINT ["/entrypoint.sh"]