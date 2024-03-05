import os, sys, yaml
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import datetime as dt

# load config file
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# import ftsreader module
sys.path.append(os.path.abspath(config['location_ftsreader']))
from ftsreader import ftsreader

# read file lists for selected block in config
site = config['selected_site']
ifglist = list(os.listdir(config[site]['ifgfolder']))
ifglist.sort()
spclist = list(os.listdir(config[site]['spcfolder']))
spclist.sort()

# check and if necessary create output folder
if not os.path.exists(config[site]['outfolder']):
    os.mkdir(config[site]['outfolder'])

# main loop over spectra
nmax = len(spclist)
for i in range(nmax):
    # use indices 2:10 for date discovery
    dd = spclist[i][2:10]
    # get start and stop dates from config
    da = dt.datetime.strptime(config[site]['datetime_start'], '%Y-%m-%d')<=dt.datetime.strptime(dd, '%Y%m%d')
    db = dt.datetime.strptime(config[site]['datetime_stop'], '%Y-%m-%d')>dt.datetime.strptime(dd, '%Y%m%d')
    spcpath = os.path.join(config[site]['spcfolder'],spclist[i])
    outfname = os.path.join(config[site]['outfolder'],spclist[i]+'.jpg')
    if os.path.exists(outfname):
        print(i,'/', nmax, '  ', spcpath, 'already exists!')
        continue
    elif not (da and db):
        print(i,'/', nmax, '  ', spcpath, 'outside date range!')
        continue
    else: 
        print(i,'/', nmax, '  ', spcpath)
    try: # to open spectrum and interferograms dependent on settings in config, choose slices or opus files
        o = ftsreader(spcpath, getspc=True, getifg=True)
        spc, spcwvn = o.spc, o.spcwvn
        if config[site]['ifgsource'] == 'spcfiles':
            ifgpath = os.path.join(config[site]['ifgfolder'],spclist[i])
            ifg = o.ifg
            extra_ifg = False
        elif config[site]['ifgsource'] == 'slices':
            ifgpath = os.path.join(config[site]['ifgfolder'], eval(config[site]['convert_spc_filename_to_ifg'])(spclist[i]))
            o2 = ftsreader(ifgpath, getslices=True)
            ifg = o2.ifg
            extra_ifg = True
        elif config[site]['ifgsource'] == 'ifgfiles':
            ifgpath = os.path.join(config[site]['ifgfolder'],spclist[i])
            o2 = ftsreader(ifgpath, getifg=True)
            ifg = o2.ifg
            extra_ifg = True
        else:
            print('ifgsource:', config[site]['ifgsource'], 'not implemented!')
        S = {}
        for k in o.header.keys():
            S[k] = ''
            k2s = list(o.header[k].keys())
            k2s.sort()
            for k2 in k2s:
                S[k]+='    '+k2+' :  '+str(o.header[k][k2])+'\n'
        
        if extra_ifg:
            for k in o2.header:
                S[k] = ''
                k2s = list(o2.header[k].keys())
                k2s.sort()
                for k2 in k2s:
                    S[k]+='    '+k2+' :  '+str(o2.header[k][k2])+'\n'
        else: pass
        #
        # prepare string to display header params
        S1 = 'Instrument Parameters\n'+S['Instrument Parameters']+'\nOptic Parameters\n'+S['Optic Parameters']+'\nFT Parameters\n'+S['FT Parameters']+'\nAcquisition Parameters\n'+S['Acquisition Parameters']
        S2 = 'Data Parameters IgSm\n'+S['Data Parameters IgSm']+'\nData Parameters SpSm\n'+S['Data Parameters SpSm']+'\nSample Parameters\n'+S['Sample Parameters']
        #
        # use pkl parameter to determine ZPD location
        pkl = o.header['Instrument Parameters']['PKL']
        #
        # plot figure
        fig = plt.figure(constrained_layout=True, figsize=(14,10))
        gs = GridSpec(4, 4, figure=fig)
        ax_txt = fig.add_subplot(gs[:, 2:])
        ax_txt.set_xticklabels([])
        ax_txt.set_yticklabels([])
        ax_txt.set_xticks([])
        ax_txt.set_yticks([])
        ax_spc = fig.add_subplot(gs[0, :2])
        ax_ifg = fig.add_subplot(gs[2, :2])
        ax_sp1 = fig.add_subplot(gs[1, 0])
        ax_sp2 = fig.add_subplot(gs[1, 1], sharey=ax_sp1)
        ax_pk1 = fig.add_subplot(gs[3, 0])
        ax_pk2 = fig.add_subplot(gs[3, 1], sharey=ax_pk1)
        # plot header params text block
        ax_txt.text(1.1, 0.6, S1, transform=ax_spc.transAxes, fontsize=7, verticalalignment='top',horizontalalignment='left') #, bbox=props)
        ax_txt.text(1.6, 0.6, S2, transform=ax_spc.transAxes, fontsize=7, verticalalignment='top',horizontalalignment='left') #, bbox=props)
        ax_txt.text(1.1, 0.94, 'Spectrum: '+spcpath+'\n\nInterferogram: '+ifgpath, transform=ax_spc.transAxes, fontsize=7, verticalalignment='top', horizontalalignment='left') #, bbox=props)
        # plot spectrum
        ax_spc.plot(spcwvn, spc, 'k-')
        ax_sp1.set_xlim(config['window_1'])
        c1 = (spcwvn>config['window_1'][1]) & (spcwvn<config['window_1'][0])
        ax_sp1.plot(spcwvn[c1], spc[c1], 'k-')
        c2 = (spcwvn>config['window_2'][1]) & (spcwvn<config['window_2'][0])
        ax_sp2.set_xlim(config['window_2'])
        ax_sp2.plot(spcwvn[c2], spc[c2], 'k-')
        # plot ifg
        ax_ifg.plot(ifg, 'k-')
        m = np.mean(ifg)
        st = config['sigma_factor']*np.std(ifg) # zoom level for ifg overview
        ax_ifg.set_ylim(m-st, m+st)
        z1, z2 = pkl-config['width_zpd'], pkl+config['width_zpd']
        ax_pk1.plot(np.arange(len(ifg))[z1:z2], ifg[z1:z2], 'k-')
        ax_pk2.plot(np.arange(len(ifg))[-z2:-z1], ifg[-z2:-z1], 'k-')
        # save figure to output folder
        fig.savefig(outfname, dpi=72)
        plt.close() 
        # maybe make garbage collection work it's magic a bit more efficiently? delete file objects
        del o
        if extra_ifg: del o2
    except Exception as e:
        print(e)

print('Done.')
