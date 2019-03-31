import numpy as np
import utils.generate_utils as gen

def upscale_nearest( x, n = 3 ):
    '''

    :param x: a bidimensional image
    :param n: the upscaling factor
    :return:
    '''

    x_prime = np.repeat(x,n,axis=1)
    x_prime = np.repeat(x_prime,n,axis=0)
    return x_prime


def upscale_with_circle( x, n = 3, bg = 0):
    '''

    :param x: a bidimensional image
    :param n: the upscaling factor
    :return:
    '''

    circle = gen.circle((n,n))
    return upscale_with_shape(x,circle,bg)


def upscale_with_shape( x, shape, bg = 0):
    '''

    :param x: a bidimensional image
    :param n: the upscaling factor
    :return:
    '''

    height,width = x.shape
    shape_h,shape_w = shape.shape
    new_img = np.ones((height*shape_h,width*shape_w),dtype=x.dtype)*bg
    for i in range(height):
        for j in range(width):
            new_img[i*shape_h:(i+1)*shape_h,j*shape_w:(j+1)*shape_w] = shape*x[i,j]

    return new_img


def normalize_tensor(t,use_negative = False):
    mn = t.min()
    mx = t.max()
    if mn == mx:
        return np.zeros_like(t,dtype='float32')
    else:
        result = np.copy(t).astype('float32')
        result -= mn
        result /= (mx-mn)

        if use_negative is True:
            result = (result - 0.5)*2

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



def get_dmd_data_matrices(X):
    return np.copy(X[:,:-1]),np.copy(X[:,1:])


def calculate_dmd(y, k=3,
           return_amplitudes = False,
           return_c = False, list_motions = None):
    '''

    :param y: is of shape [N of DOFS][N of frames]
    :param k: the compression factor, -1 -> full decomposition possible
    :return: first k eigenvalues, first k dynamic modes
    '''

    if list_motions is None:
        y_0, y_1 = get_dmd_data_matrices(y)
    else:
        start = 0
        list_y_0 = []
        list_y_1 = []
        for m in list_motions:
            motion = y[:,start:start+m]
            m_y_0,m_y_1 = get_dmd_data_matrices(motion)
            list_y_0 += [m_y_0]
            list_y_1 += [m_y_1]
            start += m
        y_0 = np.hstack(list_y_0)
        y_1 = np.hstack(list_y_1)

    u, s, v_h = calculate_truncated_svd(y_0, k)
    s_inverse = 1 / s
    v = np.array(np.matrix(v_h).getH())
    u_h = np.array(np.matrix(u).getH())

    m = y_1 @ (v * s_inverse)
    a_tilde = u_h @ m

    l, w_tilde = calculate_eigendecomposition(a_tilde)
    l_non_zero = np.abs(l) > 1e-5

    w_tilde = w_tilde[:,l_non_zero]
    l = l[l_non_zero]
    l_inverse = 1 / l

    w = l_inverse * (y_1 @ (v * s_inverse[None,:]) @ w_tilde)
    return_list = [l,w]

    if return_amplitudes is True:
        theta_plus = np.linalg.pinv(w)
        x_1 = y_1[:,0]
        a = ( l_inverse[:,None] * theta_plus ) @ x_1
        return_list += [a]

    if return_c is True:
        r0 = l_inverse.shape[0]
        t = np.tile(l,r0).reshape(r0,-1)
        t = l[:,None] - t
        np.fill_diagonal(t,1)
        t = 1/t
        t = np.prod(t,axis=1)
        c0 = -np.sum( l_inverse * t)
        return_list += [c0]

    return return_list

def calculate_truncated_svd(A,k):
    u,s,v = np.linalg.svd(A,full_matrices=False)

    if k == -1:
        return u,s,v
    else:
        return u[:,:k],s[:k],v[:k,:]

def calculate_eigendecomposition(X):
    return np.linalg.eig(X)


def reconstruct_from_dmd(
        l,w,a,c0=0,
        q=0,num_samples=1):
    '''
    :param x: the matrix with the data in the columns
    :param w: the modes of the DMD
    :param l: the eigenvalues of the DMD
    :param a: the amplitudes
    :return: the reconstructed signal
    '''

    result = np.zeros((w.shape[0],num_samples),dtype = 'complex64')

    result[:,0] = np.sum( a * w, axis=1 ) + c0*q

    for k in range(1,num_samples):
        result[:,k] = np.sum( (l**k * a) * w,axis=1)

    return result


