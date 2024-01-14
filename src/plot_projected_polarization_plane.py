import numpy as np
import matplotlib.pyplot as plt
from calc_dispersion_in_cold_plasma import calc_dispersion_relation, calc_amp_ratio
import os
import csv


def calc_angle_b0_antenna(spinPlaneNormalVec, antennaVec):
    """
    背景磁場をz軸方向とする座標系でのアンテナベクトルと背景磁場のなす角を計算する
    Document: ../doc/kvectorEstimation.md
    Args:
        spinPlaneNormalVec (np.ndarray): spin plane normal vector, 1D array, shape=(3,)
        antennaVec (np.ndarray): antenna vector, 2D array, shape=(3, spinPhaseStep)
    Returns:
        angleB0Antenna (np.ndarray): angle between B0 and antenna
    """
    b0CdotAntenna = np.dot(antennaVec.T, np.array([0, 0, 1]))
    angleB0Antenna = np.arccos(b0CdotAntenna)
    # angleB0Antennaは-pi~piの範囲で求めたいので、正負を決めるためにベクトル計算をする
    b0CrossAntenna = np.cross(antennaVec.T, np.array([0, 0, 1]))
    b0CrossAntennaCdotZ = np.dot(b0CrossAntenna, spinPlaneNormalVec)
    angleB0AntennaSigned = np.where(b0CrossAntennaCdotZ < 0, angleB0Antenna, -angleB0Antenna) # -pi~pi, rad
    return angleB0AntennaSigned # rad

def plot_projected_polarization_plane(theta, wna, phi, freq, B0, dens, densRatio, mode, outputDir):
    """
    入力パラメータを用いてプラズマ波動の偏波面を計算し、衛星のスピン面でどのように観測されるかを模擬する。
    電場強度、磁場強度が最大になるときの各アンテナの角度EmaxAngle, BmaxAngleを返す。
    Args:
        theta: angle between spin plane normal vector and z axis [deg]
        wna: wave normal angle [deg]
        phi: azimuth angle of k vector [deg]
        freq: wave frequency [Hz]
        B0: background magnetic field strength [nT]
        dens: plasma density [m^-3]
        densRatio: ratio of each ion species
        mode: 'l' or 'r'
        outputDir: output directory name, str
    Return:
        None or (EmaxAngleRounded, BmaxAngleRounded)
    """
    print('calc for these parameters:')
    print('theta:', theta)
    print('phi:', phi)
    print('wna:', wna)
    print('freq:', freq)
    print('mode:', mode)
    # 定数
    spinPhaseStep  = 36
    wavePhaseStep = 360
    # calc wave field vectors
    wna = wna
    freq = freq  # Hz
    angle_freq = 2*np.pi*freq

    k_vec = np.array([np.sin(wna*np.pi/180), 0, np.cos(wna*np.pi/180)])
    n_L, n_R, S, D, P = calc_dispersion_relation(angle_freq, wna, B0, dens, densRatio)
    if mode == 'l':
        if np.isnan(n_L) == True:
            print('No valid value for', f'freq={freq}, mode={mode}')
            return np.nan, np.nan
        # left hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, _ = calc_amp_ratio(n_L, S, D, P, wna)
    elif mode == 'r':
        if np.isnan(n_R) == True:
            print('No valid value for', f'freq={freq}, mode={mode}')
            return np.nan, np.nan
        # right hand circular polarization
        Ey_Ex, Ez_Ex, By_Bx, Bz_Bx, _ = calc_amp_ratio(n_R, S, D, P, wna)

    # アンテナベクトルの設定
    EantennaBaseVecInSCSys = np.array([-np.sin(np.deg2rad(35)), np.cos(np.deg2rad(35)), 0])  # 衛星座標系
    sBantennaBaseVecInSCSys = np.array([0, -1.0, 0]) # 衛星座標系
    BloopantennaBaseVecInSCSys = np.array([2**-0.5, -3**-0.5, 6**-0.5]) # 衛星座標系

    spinPhase = np.linspace(0, 2*np.pi, spinPhaseStep, endpoint=False)
    # それぞれのスピン位相での衛星座標系でのアンテナベクトルを計算する
    zaxisRotationMatrix = np.array([[np.cos(spinPhase), -np.sin(spinPhase), np.zeros(len(spinPhase))],
                                    [np.sin(spinPhase), np.cos(spinPhase), np.zeros(len(spinPhase))],
                                    [np.zeros(len(spinPhase)), np.zeros(len(spinPhase)), np.ones(len(spinPhase))]])
    EantennaVec = np.zeros((3, len(spinPhase)))
    BantennaVec = np.zeros((3, len(spinPhase)))
    for i in range(len(spinPhase)):
        EantennaVecInSCSys = np.dot(zaxisRotationMatrix[:, :, i], EantennaBaseVecInSCSys)
        if freq < 1000:
            BantennaVecInSCSys = np.dot(zaxisRotationMatrix[:, :, i], sBantennaBaseVecInSCSys)
        else:
            BantennaVecInSCSys = np.dot(zaxisRotationMatrix[:, :, i], BloopantennaBaseVecInSCSys)

        # 衛星座標系でのアンテナベクトルを地球座標系でのアンテナベクトルに変換する
        # 地球座標系:z軸が磁力線方向、x-z面にスピン軸がある
        yaxisRotationMatrix = np.array([[np.cos(np.deg2rad(theta)), 0, np.sin(np.deg2rad(theta))],
                                        [0, 1, 0],
                                        [-np.sin(np.deg2rad(theta)), 0, np.cos(np.deg2rad(theta))]])
        EantennaVec[:, i] = np.dot(yaxisRotationMatrix, EantennaVecInSCSys)
        BantennaVec[:, i] = np.dot(yaxisRotationMatrix, BantennaVecInSCSys)

    # 波動ベクトルの計算
    phase = np.linspace(0, 2*np.pi, wavePhaseStep, endpoint=False)
    EwVec = np.array([np.cos(phase), Ey_Ex*np.sin(phase), Ez_Ex*np.cos(phase)])
    BwVec = np.array([np.cos(phase), By_Bx*np.sin(phase), Bz_Bx*np.cos(phase)])
    # 方位角phiの回転行列で波動ベクトルを回転させる
    phiRotationMatrix = np.array([[np.cos(np.deg2rad(phi)), -np.sin(np.deg2rad(phi)), 0],
                                  [np.sin(np.deg2rad(phi)), np.cos(np.deg2rad(phi)), 0],
                                  [0, 0, 1]])
    for i in range(len(phase)):
        EwVec[:, i] = np.dot(phiRotationMatrix, EwVec[:, i])
        BwVec[:, i] = np.dot(phiRotationMatrix, BwVec[:, i])

    # 各スピン位相で計測される電場強度、磁場強度を計算する
    EpwrObs = np.zeros(len(spinPhase))
    BpwrObs = np.zeros(len(spinPhase))
    for i in range(len(spinPhase)):
        EvecDotAntenna = np.dot(EantennaVec[:, i], EwVec)
        EampObs = np.nanmax(EvecDotAntenna)  # スピン周期より波動周期のほうが短いので、最大値を取る
        EpwrObs[i] = EampObs**2
        BvecDotAntenna = np.dot(BantennaVec[:, i], BwVec)
        BampObs = np.nanmax(BvecDotAntenna)  # スピン周期より波動周期のほうが短いので、最大値を取る
        BpwrObs[i] = BampObs**2

    # アンテナと背景磁場(z軸)のなす角を計算する
    spinPlaneNormalVec = np.array([np.sin(np.deg2rad(theta)), 0, np.cos(np.deg2rad(theta))])
    angleB0E = calc_angle_b0_antenna(spinPlaneNormalVec, EantennaVec)
    angleB0B = calc_angle_b0_antenna(spinPlaneNormalVec, BantennaVec)
    # rad -> deg
    angleB0E = np.rad2deg(angleB0E)
    angleB0B = np.rad2deg(angleB0B)

    # スピン軸、偏波面の3Dプロットと角度vs電場強度、磁場強度のプロット
    k_vec_rotated = np.dot(phiRotationMatrix, k_vec)
    fig = plt.figure(figsize=(24, 12))
    gs = fig.add_gridspec(2, 4)
    ax1 = fig.add_subplot(gs[:2, :2], projection='3d')
    ax2 = fig.add_subplot(gs[0, 2])
    ax3 = fig.add_subplot(gs[0, 3])
    ax4 = fig.add_subplot(gs[1, 2])
    ax5 = fig.add_subplot(gs[1, 3])
    # 3D plot
    ax1.quiver(0, 0, 0,
                spinPlaneNormalVec[0], spinPlaneNormalVec[1], spinPlaneNormalVec[2],
                color='k', label='spin plane normal vector')
    ax1.quiver(0, 0, 0,
                k_vec_rotated[0], k_vec_rotated[1], k_vec_rotated[2],
                color='g', label='k vector ({0}, {1})'.format(str(wna), str(phi)))
    ax1.scatter(EantennaVec[0], EantennaVec[1], EantennaVec[2],
                color='lightcoral', label='E antenna')
    ax1.scatter(BantennaVec[0], BantennaVec[1], BantennaVec[2],
                color='lightblue', label='B antenna')
    ax1.scatter(EwVec[0], EwVec[1], EwVec[2],
                color='r', label='E wave')
    ax1.scatter(BwVec[0], BwVec[1], BwVec[2],
                color='b', label='B wave')

    ax1.set_xlim(-2.5, 2.5)
    ax1.set_ylim(-2.5, 2.5)
    ax1.set_zlim(-2.5, 2.5)
    ax1.set_xlabel('x')
    ax1.set_ylabel('y')
    ax1.set_zlabel('z (B0)')
    ax1.view_init(elev=30, azim=45)
    ax1.set_aspect('equal')
    ax1.set_title('theta={0}, phi={1}, wna={2}, freq={3}'.format(str(theta), str(phi), str(wna), str(freq)))
    # legend position
    ax1.legend(loc='lower right')

    # angle vs power plot (0-180 deg) for E field
    angleB0E_folded = np.where(angleB0E > 0, angleB0E, angleB0E+180)
    ax2.scatter(angleB0E_folded, EpwrObs, color='r', label='E field')
    ax2.set_xlim(0, 180)
    # y軸の下限は0
    ax2.set_ylim(bottom=0)
    ax2.set_xticks([0, 45, 90, 135, 180])
    ax2.set_xlabel('angle')
    ax2.set_ylabel('Normalized power \n Eobs^2/Ex^2')
    ax2.legend(loc='upper right')

    # angle vs power plot (0-180 deg) for B field
    angleB0B_folded = np.where(angleB0B > 0, angleB0B, angleB0B+180)
    ax3.scatter(angleB0B_folded, BpwrObs, color='b', label='B field')
    ax3.set_xlim(0, 180)
    # y軸の下限は0
    ax3.set_ylim(bottom=0)
    ax3.set_xticks([0, 45, 90, 135, 180])
    ax3.set_xlabel('angle')
    ax3.set_ylabel('Normalized power \n Bobs^2/Bx^2')
    ax3.legend(loc='upper right')

    # angle vs power plot (-180 - 180 deg) for E field
    ax4.scatter(angleB0E, EpwrObs, color='r', label='E field')
    ax4.set_xlim(-180, 180)
    # y軸の下限は0
    ax4.set_ylim(bottom=0)
    ax4.set_xticks([-180, -135, -90, -45, 0, 45, 90, 135, 180])
    ax4.set_xlabel('angle')
    ax4.set_ylabel('Normalized power \n Eobs^2/Ex^2')
    ax4.legend(loc='upper right')

    # angle vs power plot (-180 - 180 deg) for B field
    ax5.scatter(angleB0B, BpwrObs, color='b', label='B field')
    ax5.set_xlim(-180, 180)
    # y軸の下限は0
    ax5.set_ylim(bottom=0)
    ax5.set_xticks([-180, -135, -90, -45, 0, 45, 90, 135, 180])
    ax5.set_xlabel('angle')
    ax5.set_ylabel('Normalized power \n Bobs^2/Bx^2')
    ax5.legend(loc='upper right')

    # save figure
    if mode == 'l':
        savefig_dir = '../plots/projected_polarization_plane/'+outputDir+'/left_hand_circular_test/theta'+str(theta)+'/freq'+str(freq)+'/wna'+str(wna)+'/'
    elif mode == 'r':
        savefig_dir = '../plots/projected_polarization_plane/'+outputDir+'/right_hand_circular_test/theta'+str(theta)+'/freq'+str(freq)+'/wna'+str(wna)+'/'

    os.makedirs(savefig_dir, exist_ok=True)
    plt.savefig(savefig_dir+'phi'+str(phi)+'.jpeg', dpi=300)
    plt.close()

    # find max power angle
    Emax_angle = np.rad2deg(angleB0E_folded[np.argmax(EpwrObs)])
    Bmax_angle = np.rad2deg(angleB0B_folded[np.argmax(BpwrObs)])
    # 第3位を四捨五入した値を返す
    EmaxAngleRounded = round(Emax_angle, 2)
    BmaxAngleRounded = round(Bmax_angle, 2)
    return EmaxAngleRounded, BmaxAngleRounded


wnaAry = np.array([0, 10, 20, 30, 40, 50, 60,
                    70, 80, 100, 110, 120,
                    130, 140, 150, 160, 170, 180])
phiAry = np.arange(0, 360, 10)
freqList = [3.16, 5.62, 10, 17.8,
            31.6, 56.2, 100, 178,
            316, 562, 1000, 1780,
            3160]

saveDir = '../execute/SimulatedObservation/'
outputDir = 'event6'
os.makedirs(saveDir+outputDir+'/', exist_ok=True)
B0 = 8410 # nT
dens = 60e6 # m^-3
densRatio = np.array([0.46, 0.11, 0.43]) # H:He:O
theta = 114 # deg
# 設定をtxtに保存
with open(saveDir+outputDir+'/setting.txt', 'w') as f:
    f.write('B0: '+str(B0)+' nT\n')
    f.write('dens: '+str(dens)+' m^-3\n')
    f.write('densRatio: '+str(densRatio)+'\n')
    f.write('theta: '+str(theta)+' deg\n')
    f.write('wnaAry: '+str(wnaAry)+'\n')
    f.write('phiAry: '+str(phiAry)+'\n')
    f.write('freqList: '+str(freqList)+'\n')

for mode in ['r', 'l']:
    for freq in freqList:
        # wna_listとphi_listの最初の値で計算を行い、np.nanが返ってきたら計算を行わない
        wna = wnaAry[0]
        phi = phiAry[0]
        EmaxAngleTest, BmaxAngleTest = plot_projected_polarization_plane(theta, wna, phi, freq, B0, dens, densRatio, mode, outputDir)
        if np.isnan(EmaxAngleTest) == True or np.isnan(BmaxAngleTest) == True:
            print('No valid value for', f'freq={freq}, mode={mode}')
            continue
        # 返り値がFalseでない場合は、計算を行う
        os.makedirs(saveDir+outputDir+'/', exist_ok=True)
        csvSaveName = saveDir+outputDir+'/pyEmax_Bmax_angle_freq-{}_mode-{}.csv'
        with open(csvSaveName.format(freq, mode), 'a') as f:
            writer = csv.writer(f)
            writer.writerow([""]+phiAry.tolist())
            for wna in wnaAry:
                anglePairsList = []
                for phi in phiAry:
                    EmaxAngle, BmaxAngle = plot_projected_polarization_plane(theta, wna, phi, freq, B0, dens, densRatio, mode, outputDir)
                    anglePairsList.append(str(EmaxAngle)+'v'+str(BmaxAngle))
                writer.writerow([wna]+anglePairsList)
