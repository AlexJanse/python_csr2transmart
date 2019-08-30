import os
from typing import Optional, Sequence

from sources2csr.ngs import NGS, LibraryStrategy
from sources2csr.ngs_reader import NgsReader, NgsReaderException, NgsFileReader


class NgsMafReader(NgsReader):
    """ Mutation data reader.
        Parses NGS files in the MAF format. The MAF files are gzipped.
    """

    def __init__(self, input_dir: str):
        super().__init__(input_dir, LibraryStrategy.SNV)
        self.sample_id_column_name = 'Tumor_Sample_Barcode'

    def read_data(self, filename: str) -> Optional[Sequence[NGS]]:
        """ Reads .maf.gz. file.
        Sample_id should be specified in the :attr:`self.sample_id_column_name` column.

        :param filename: name of the input file
        :return: Sequence of NGS objects
        """
        data = NgsFileReader(os.path.join(self.input_dir, filename)).read_data()
        print(data)
        biosource_biomaterial_dict = dict()
        if len(data) > 1:
            for row in data:
                try:
                    col_value = row[self.sample_id_column_name]
                except KeyError:
                    raise NgsReaderException("Invalid {} file. No column with name {}. Cannot read sample ids."
                                             .format(filename, self.sample_id_column_name))
                biosource_biomaterial = self.biosource_biomaterial_from_sample_id(col_value, filename)
                biosource_biomaterial_dict.setdefault(biosource_biomaterial[0], []).append(biosource_biomaterial[1])
        else:
            raise NgsReaderException("Cannot read NGS data from file: {}. Empty data.".format(filename))
        return self.map_ngs(biosource_biomaterial_dict, filename)
