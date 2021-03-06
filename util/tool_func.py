import numpy as np
from scipy.spatial.transform import Rotation as R

def filterTraj(traj_xyz, fit_time=None, segment=20, frame_time=0.05, keep_data = False):

    if fit_time is None:
        fit_time = np.arange(len(traj_xyz)) * frame_time
    
    times = fit_time.copy()

    # 2. Spherical Linear Interpolation of Rotations.
    from scipy.spatial.transform import RotationSpline

    rotation = False
    if rotation:
        R_quats = R.from_quat(traj_xyz[:, 4: 8])
        spline = RotationSpline(times, R_quats)
        quats_plot = spline(fit_time).as_quat()

    trajs_plot = []  # 拟合后轨迹

    length = traj_xyz.shape[0]
    for i in range(0, length, segment):
        s = max(0, i-1)   # start index
        e = i+segment   # end index
        if length < e:
            s = length - segment
            e = length

        ps = s - segment//2  # filter start index
        pe = e + segment//2  # # filter end index

        if ps < 0:
            ps = 0
            pe += segment//2
        if pe > length:
            ps -= segment//2
            pe = length

        fp = np.polyfit(times[ps:pe], traj_xyz[ps:pe], 3)  # 分段拟合轨迹

        fs = 0 if s == 0 else np.where(fit_time == times[i - 1])[0][0] # 拟合轨迹到起始坐标
        fe = np.where(fit_time == times[e-1])[0][0]  # 拟合轨迹到结束坐标
        fe = fe+1 if e == length else fe

        for j in fit_time[fs: fe]:
            trajs_plot.append(np.polyval(fp, j))


    frame_id = -1 * np.ones(len(trajs_plot))
    old_id = [np.where(fit_time==t)[0][0] for t in times]
    frame_id[old_id] = old_id
    interp_idx = np.where(frame_id == -1)[0]

    frame_id = np.arange(len(trajs_plot))

    # fitLidar = np.concatenate(
    #     (frame_id.reshape(-1, 1), np.asarray(trajs_plot), quats_plot, fit_time.reshape(-1, 1)), axis=1)
    fit_traj = trajs_plot

    if keep_data:
        fit_traj[old_id] = traj_xyz

    return fit_traj
