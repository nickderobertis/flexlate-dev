#!/bin/bash
cd ..
python -m flexlate_dev.config_schema > docsrc/source/_static/config-schema.json
cd docsrc