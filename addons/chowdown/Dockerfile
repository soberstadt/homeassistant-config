ARG BUILD_FROM=
FROM $BUILD_FROM

ENV LANG C.UTF-8

ENV NOKOGIRI_USE_SYSTEM_LIBRARIES=1

RUN apk update --update \
&& apk add ruby \
           ruby-etc \
           ruby-bigdecimal \
           ruby-io-console \
           ruby-irb \
           ca-certificates \
           libressl \
           less \
           libatomic readline readline-dev libxml2 libxml2-dev \
           ncurses-terminfo-base ncurses-terminfo \
           libxslt libxslt-dev zlib-dev zlib \
           ruby-dev yaml yaml-dev \
           libffi-dev build-base git nodejs \
           ruby-json ruby-rake \
&& apk add --virtual .build-dependencies \
           build-base \
           ruby-dev \
           libressl-dev \
&& gem install bundler || apk add ruby-bundler \
&& bundle config build.nokogiri --use-system-libraries \
&& bundle config git.allow_insecure true \
&& gem install json \
\
&& gem cleanup \
&& apk del .build-dependencies \
&& rm -rf /usr/lib/ruby/gems/*/cache/* \
          /var/cache/apk/* \
          /tmp/* \
          /var/tmp/*

RUN apk add --no-cache --virtual .build-deps make gcc g++ musl-dev \
 && gem install --no-document jekyll webrick \
 && apk del .build-deps

# RUN jekyll new myblog
RUN git clone https://github.com/clarklab/chowdown.git

# Copy data for add-on
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "bash", "/run.sh" ]

EXPOSE 8099

WORKDIR /chowdown
