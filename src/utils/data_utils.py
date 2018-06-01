import numpy as np

def normalize_tensor(t):
    mn = t.min()
    mx = t.max()
    if mn == mx:
        return np.zeros_like(t)
    else:
        result = np.copy(t).astype('float64')
        result -= mn
        result /= (mx-mn)

        return result


def describe_array(
        arr,
        intro=None,
        print_full_array = False,
        identation=0,
        print_min_max = True,
        print_mean_std = True,
        print_skew_analysis = True,
        float_format = '%.2f'):

    prefix = '\t'*identation
    print(' ')
    if intro is not None:
        print(prefix+intro)

    if print_full_array == True:
        print(arr)



    mean = arr.mean()
    std = arr.std()


    if print_mean_std is True:
        print(prefix+'mean:',float_format % mean,
              ', std:', float_format % std,
              ', median:', float_format % np.median(arr),
              ', shape:', arr.shape)

    if print_skew_analysis is True:
        size_array = 1
        for i in arr.shape:
            size_array *= i

        above_mean_std = np.sum(arr >= (mean + std)) / size_array
        below_mean_std = np.sum(arr <= (mean - std)) / size_array

        print(prefix+'mean+-std:',
              float_format % (mean-std),
              '-',float_format % (mean+std))
        print(prefix+'\t% below mean-std:',float_format % below_mean_std)
        print(prefix+'\t% above mean+std:',float_format % above_mean_std)

    if print_min_max is True:
        m1 = arr.min()
        m2 = arr.max()
        print(prefix+'min:',m1,
              ', max:',m2,
              ', max - min:',float_format % (m2-m1))
        print(prefix+'position of mean:',float_format % ((mean-m1)/(m2-m1)))
    print(' ')