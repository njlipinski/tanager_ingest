from ast import literal_eval
from functools import partial, reduce
import json
from operator import or_
import os
import random
import re
import math

import django
from django.conf import settings
from django import forms
import numpy as np
import pandas as pd

django.setup()

from recipes import samples
from visor.dj_utils import are_in, djget, eta, fields
from visor.io.handlers import ingest_sample_csv
from visor.models import Database, Library, Sample, SampleType
from visor.spectral import make_filterset

# the examples in this notebook don't do risky async stuff to the database.
# they all work the exact same way on the backend as the admin console. however, 
# ipython/jupyter wraps itself in an event loop that looks scary to django. this 
# environment variable tells django to calm down about it.
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

def upload(target_dir):

    base_directory = target_dir

    print("Starting")

    subdirectories = [d for d in os.listdir(base_directory) 
                    if os.path.isdir(os.path.join(base_directory, d))]

    with open("ingest_errors.log", "w") as log_file:
        for subfolder in subdirectories:
            csv_directory = os.path.join(base_directory, subfolder) + '/'
            
            csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]
            
            if not csv_files:
                continue
        
            for ix, file in enumerate(csv_files):
                if not file.endswith('.csv'):
                    continue    

                ingest_dict = ingest_sample_csv(csv_directory + file)

                sample = ingest_dict["sample"]
                print(ingest_dict)

                if sample is None:
                    log_file.write(f"{ix}: {file} - Skipped, no sample object created.\n")
                    print("Error: sample = none")
                    continue

                try:
                    sample.clean()
                    sample.save()
                except forms.ValidationError as ve:
                    log_file.write(f"{ix}: {file} - ValidationError: {ve}\n")
                    print("Error: validation error")
                    continue
                except IndexError as ie:
                    log_file.write(f"{ix}: {file} - IndexError: {ie}\n")
                    print("Error: index error")
                    continue

                if sample.material_class:
                    sample_type_obj, created = SampleType.objects.get_or_create(name=sample.material_class)
                    sample.sample_type.add(sample_type_obj)

    print("Finished")
