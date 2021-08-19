import pandas as pd
# All of the omitted stimuli have a duration of 250ms as defined
# by the Visual Behavior team. For questions about duration contact that
# team.
from pynwb import NWBFile, ProcessingModule
from pynwb.base import Images
from pynwb.image import GrayscaleImage

from allensdk.brain_observatory.behavior.image_api import ImageApi, Image


def get_column_name(table_cols: list,
                    possible_names: set) -> str:
    """
    This function returns a column name, given a table with unknown
    column names and a set of possible column names which are expected.
    The table column name returned should be the only name contained in
    the "expected" possible names.
    :param table_cols: the table columns to search for the possible name within
    :param possible_names: the names that could exist within the data columns
    :return: the first entry of the intersection between the possible names
             and the names of the columns of the stimulus table
    """

    column_set = set(table_cols)
    column_names = list(column_set.intersection(possible_names))
    if not len(column_names) == 1:
        raise KeyError("Table expected one name column in intersection, found:"
                       f" {column_names}")
    return column_names[0]


def set_omitted_stop_time(stimulus_table: pd.DataFrame,
                          omitted_time_duration: float = 0.25) -> None:
    """
    This function sets the stop time for a row that of a stimuli table that
    is a omitted stimuli. A omitted stimuli is a stimuli where a mouse is
    shown only a grey screen and these last for 250 milliseconds. These do not
    include a stop_time or end_frame as other stimuli in the stimulus table due
    to design choices. For these stimuli to be added they must have the
    stop_time calculated and put into the row as data before writing to NWB.
    :param stimulus_table: pd.DataFrame that contains the stimuli presented to
                           an experiment subject
    :param omitted_time_duration: The duration in seconds of the expected
    length
                                  of the omitted stimuli
    :return:
          stimulus_table_row: returns the same dictionary as inputted but with
                              an additional entry for stop_time.
    """
    omitted_row_indexs = stimulus_table.index[
        stimulus_table['omitted']].tolist()
    for omitted_row_idx in omitted_row_indexs:
        row = stimulus_table.iloc[omitted_row_idx]
        start_time = row['start_time']
        end_time = start_time + omitted_time_duration
        row['stop_time'] = end_time
        row['duration'] = omitted_time_duration
        stimulus_table.iloc[omitted_row_idx] = row


def get_image(nwbfile: NWBFile, name: str, module: str) -> Image:
    nwb_img = nwbfile.processing[module].get_data_interface('images')[name]
    data = nwb_img.data
    resolution = nwb_img.resolution  # px/cm
    spacing = [resolution * 10, resolution * 10]

    img = ImageApi.serialize(data, spacing, 'mm')
    img = ImageApi.deserialize(img=img)
    return img


def add_image(nwbfile: NWBFile, image_data: Image, image_name: str):
    """
    Adds image given by image_data with name image_name to nwbfile

    Parameters
    ----------
    nwbfile
        nwbfile to add image to
    image_data
        The image data
    image_name
        Image name

    Returns
    -------
    None
    """
    module_name = 'ophys'
    description = '{} image at pixels/cm resolution'.format(image_name)

    data, spacing, unit = image_data

    assert spacing[0] == spacing[1] and len(
        spacing) == 2 and unit == 'mm'

    if module_name not in nwbfile.processing:
        ophys_mod = ProcessingModule(module_name,
                                     'Ophys processing module')
        nwbfile.add_processing_module(ophys_mod)
    else:
        ophys_mod = nwbfile.processing[module_name]

    image = GrayscaleImage(image_name,
                           data,
                           resolution=spacing[0] / 10,
                           description=description)

    if 'images' not in ophys_mod.containers:
        images = Images(name='images')
        ophys_mod.add_data_interface(images)
    else:
        images = ophys_mod['images']
    images.add_image(image)
