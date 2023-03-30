# MCA Intensity Counter
A code to count the MCA (Malti Channel Analyzer) Intensity in a certain region between two dates.

## Libraries Used
- load
- pytplot
- pyspedas
- matplotlib.pyplot
- numpy
- pandas
## Functions
- get_date_list
Takes a start date and end date as input and returns a list of dates in between them with daily frequency.

- count_mca_intnsity
This function takes start date, end date, postgap and altitude range as input, performs some analysis and returns the MCA Intensity in a certain region.

## Analysis
- Get a list of dates from start_date to end_date using get_date_list function.
- Define E_matrix and B_matrix as empty matrices to store the MCA Intensity for each date.
- Define freq_array and intensity_array.
- For each date in the date list:
  - Load MCA data using load.mca function.
  - Try to load orbit data using load.orb function. If it fails, move to the next date.
  - Interpolate the data to get the ILAT, MLAT, MLT and ALT values.
  - Get the values of E_array and B_array using get_data function.
  - Get the index of target region using np.where function.
  - Get the MCA Intensity in the target region.
  - For each frequency and intensity, count the number of instances and add it to E_matrix_per_day and B_matrix_per_day.
  - Add E_matrix_per_day and B_matrix_per_day to E_matrix and B_matrix respectively.
