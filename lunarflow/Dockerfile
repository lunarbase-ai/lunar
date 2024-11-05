# Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

FROM node:18-bookworm as base
RUN apt update && apt install -y g++ make build-essential
WORKDIR /app
COPY package*.json ./
RUN yarn install

FROM base as builder
WORKDIR /app
COPY . .

RUN yarn build

FROM base as production
WORKDIR /app

RUN printf 'NEXT_PUBLIC_LUNARVERSE_ADDRESS=http://0.0.0.0:8088\n \
NEXT_PUBLIC_HOST=http://localhost:8080\n \
NEXTAUTH_URL=http://localhost:8080\n \
NEXTAUTH_SECRET=secret\n \
BYPASS_AUTHENTICATION=true\n \
DEFAULT_USER_PROFILE=admin' > /app/.env

# Create a group 'nodejs' with GID 1001
RUN groupadd -g 1001 nodejs
# Create a user 'nextjs' with UID 1001 and add it to the 'nodejs' group
RUN useradd -r -u 1001 -g nodejs nextjs
USER nextjs

COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 8080
CMD yarn start

