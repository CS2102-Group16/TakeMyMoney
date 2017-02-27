class Helper:


    @staticmethod
    def db_rows_to_dict(attrs, rows):
        """
        Convert DB rows to a list of dicts
        NOTE: you must ensure that the sequence in attrs matches that of the rows

        :param attrs: Attributes to be SELECTed
        :param rows: rows returned by the db
        :return: list of dicts
        """
        objects = []
        for row in rows:
            object = {}
            for i in range(len(attrs)):
                object[attrs[i]] = row[i]
            objects.append(object)
        return objects
