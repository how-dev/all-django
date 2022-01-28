import csv
import io

import pandas as pd
from django.http import HttpResponse


class DBToFile:
    def __init__(self):
        pass

    supported_files_types = ("xlsx", "csv")
    csv_fields = ("id",)

    @staticmethod
    def convert_file_to_excel(data_frame, file_name):
        bio = io.BytesIO()
        writer = pd.ExcelWriter(bio, engine="xlsxwriter")
        data_frame.to_excel(writer, f"{file_name}.xlsx", index=False)
        writer.save()
        bio.seek(0)

        excel_file = bio.read()

        return excel_file

    def create_excel_file(self, resources, file_name):
        resource = resources()
        dataset = resource.export()
        df = pd.read_excel(dataset.xlsx)

        excel_file = self.convert_file_to_excel(df, file_name)

        return excel_file

    @staticmethod
    def http_csv(fields, queryset, serializer, file_name):
        response = HttpResponse(content_type="text/csv")
        writer = csv.DictWriter(response, fieldnames=fields)
        writer.writeheader()

        data = serializer(queryset, many=True).data

        for row in data:
            writer.writerow(row)

        response["Content-Disposition"] = f'attachment; filename="{file_name}.csv"'

        return response

    def http_excel(self, resources, file_name):
        excel_file = self.create_excel_file(resources, file_name)
        response = HttpResponse(excel_file, content_type="application/vnd.ms-excel")
        response["Content-Disposition"] = f'attachment; filename="{file_name}.xlsx"'

        return response

    def is_supported(self, file_type):
        return file_type in self.supported_files_types
