import os
import numpy as np
from matplotlib import cm, colors

from .io import load_file
from .spaces import get_mapping, get_mask


PLOT_MAPPING = {
    surf_type: load_file(os.path.join(
        '2d_plotting_data', f'onavg-ico128_to_{surf_type}_image.npy'))
    for surf_type in ['inflated', 'pial', 'midthickness', 'white']}


def unmask_and_upsample(values, space, mask, nn=True):
    ico = int(space.split('-ico')[1])
    nv = ico**2 * 10 + 2

    new_values = []
    for v, lr in zip(values, 'lr'):
        if mask is not None and mask is not False:
            if isinstance(mask, (tuple, list)) and \
                    all([isinstance(_, np.ndarray) for _ in mask]):
                m = mask['lr'.index(lr)]
            else:
                m = get_mask(lr, space)
            vv = np.full((nv, ) + v.shape[1:], np.nan)
            vv[m] = v
        else:
            vv = v

        mapping = get_mapping(lr, space, 'onavg-ico128', nn=nn)
        vv = mapping.T @ vv

        new_values.append(vv)

    new_values = np.concatenate(new_values, axis=0)
    return new_values


def to_color(values, cmap, vmax=None, vmin=None):
    if vmin is None:
        vmin = -vmax
    r = (values - vmin) / (vmax - vmin)
    r = np.clip(r, 0.0, 1.0)
    cmap = cm.get_cmap(cmap)
    c = cmap(r)
    return c


def prepare_data(
        values, space, mask, nn=True, cmap=None, vmax=None, vmin=None, return_scale=False,
        medial_wall_color=[0.8, 0.8, 0.8, 1.0], background_color=[1.0, 1.0, 1.0, 0.0]):

    values = unmask_and_upsample(values, space, mask, nn=nn)

    if cmap is not None:
        nan_mask = np.isnan(values)
        values = to_color(values, cmap, vmax, vmin)
        values[nan_mask] = medial_wall_color
        values = np.concatenate([values, [_[:values.shape[1]] for _ in [medial_wall_color, background_color]]], axis=0)

        if return_scale:
            norm = colors.Normalize(vmax=vmax, vmin=vmin, clip=True)
            scale = cm.ScalarMappable(norm=norm, cmap=cmap)
            return values, scale

    return values


# def brain_plot(prepared_values, surf_type='inflated'):
#     img = prepared_values[PLOT_MAPPING[surf_type]]
#     return img


def brain_plot(values, space, mask, surf_type='inflated', nn=True, cmap=None, vmax=None, vmin=None, return_scale=False,
               medial_wall_color=[0.8, 0.8, 0.8, 1.0], background_color=[1.0, 1.0, 1.0, 0.0]):
    ret = prepare_data(
        values, space, mask, nn=nn, cmap=cmap, vmax=vmax, vmin=vmin,
        return_scale=return_scale, medial_wall_color=medial_wall_color,
        background_color=background_color)
    if return_scale:
        prepared_values, scale = ret
    else:
        prepared_values = ret

    img = prepared_values[PLOT_MAPPING[surf_type]]

    if return_scale:
        return img, scale
    return img
