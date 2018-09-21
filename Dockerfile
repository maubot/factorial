FROM maubot/plugin-base AS builder

COPY . /go/src/maubot.xyz/factorial
RUN go build -buildmode=plugin -o /maubot-plugins/factorial.mbp maubot.xyz/factorial

FROM alpine:latest
COPY --from=builder /maubot-plugins/factorial.mbp /maubot-plugins/factorial.mbp
VOLUME /output
CMD ["cp", "/maubot-plugins/factorial.mbp", "/output/factorial.mbp"]
