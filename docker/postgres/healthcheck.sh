#!/bin/bash

pg_isready -q -d "${POSTGRES_DB}" -U "${POSTGRES_USER}" || exit 1