import numpy as np
# visual or imagery
task = "visual"

# fmin fmax for psd
#start = 1
#stop = 40
#window = 1
#fmin_s = 0.01
#fmin = np.arange(start,stop,window)
#fmin_range = np.concatenate(fmin_s,fmin)
#[0.01,4,7,12,30]
#np.arange(start,stop,window)
#[0.01,4,7,12,30]
#fmax_range = np.arange(start+window,stop+window,window)
#np.arange(1,40,1)
#[4,7,12,30,50]
# test or real_test
import numpy as np
start = 1
stop = 41
window = 1
fmin_s = np.array(0.01)
fmin = np.arange(start,stop,window)
fmin_range = np.append(fmin_s,fmin)
#[0.01,4,7,12,30]
#np.arange(start,stop,window)
#[0.01,4,7,12,30]
fmax_range = np.arange(start,stop,window)
#np.arange(1,40,1)
#[4,7,12,30,50]
# test or real_test

#for i in range(len(fmax_range)):
#    print(fmin_range[i],fmax_range[i])
    
test_type = "test"

files = [
"1-Chaichan_1_2021-04-07-06.24.14",
#"2-Dipesh_2_2021-04-07-07.19.01",
#'3-Witoon_3_2021-04-07-08.24.44',
#"4-Suhel_1_2021-04-09-07.17.43",
#"5-Siraphat_2_2021-04-07-11.55.30",
#"6-Nuttasit_3_2021-04-07-12.34.46",
#"7-Suyogya_1_2021-04-08-08.42.34",
#"8-Alok_2_2021-04-08-09.27.31",
#"9-Flim_3_2021-04-08-10.21.20",
#"10-View_1_2021-04-08-11.03.34",
#"11-Pumphat_2_2021-04-08-12.09.09",
#"12-Nuclear_3_2021-04-09-06.37.36",
#"13-Suhel_1_2021-04-09-07.17.43",
#"14-Gon_2_2021-04-09-08.15.26",
#"15-Aung_3_2021-04-09-08.57.37",
#"16-Rom_1_2021-04-09-10.33.02",
#"17-Tawan_2_2021-04-09-11.13.20",
#"18-Arthit_3_2021-04-09-11.56.29",
#"19-Ankit_1_2021-04-09-12.27.22",
#"20-Name_2_2021-04-09-13.54.06",
]
