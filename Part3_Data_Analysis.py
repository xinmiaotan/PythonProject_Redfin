import json
import pylab as plb
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from scipy.interpolate import griddata

#location for file downloaded
HOME_DIR = "/Users/xinmiaotan/PycharmProjects/PythonBerkeley/data"

#read in metadata_map_for_analysis
def read_metadata(dataname):
    meta_data_path = "%s/all*%s" % (HOME_DIR, dataname)
    with open(meta_data_path) as f:
        meta_data = json.load(f)
        return meta_data

metadata_map_for_analysis = read_metadata('metadatamap_for_analysis')

#check the style category: 'Single Family Residential', 'Townhouse', 'Condo'
def var_check(data,var):
    var_map = []
    for item in data:
        if data[item][var] not in var_map:
            var_map.append(data[item][var])
    return sorted(var_map)

print(var_check(metadata_map_for_analysis, 'style'))
print(var_check(metadata_map_for_analysis, 'year_month'))
print(var_check(metadata_map_for_analysis, 'zipcode'))

#seperate metadata_map_for_analysis into sfh, townhouse and condo

metadata_map_for_analysis_sfh ={}
metadata_map_for_analysis_townhouse={}
metadata_map_for_analysis_condo={}

for item in metadata_map_for_analysis:
    if metadata_map_for_analysis[item]['style'] == 'Single Family Residential':
        metadata_map_for_analysis_sfh[item] = metadata_map_for_analysis[item]
    if metadata_map_for_analysis[item]['style'] == 'Townhouse':
        metadata_map_for_analysis_townhouse[item] = metadata_map_for_analysis[item]
    if metadata_map_for_analysis[item]['style'] == 'Condo/Co-op':
        metadata_map_for_analysis_condo[item] = metadata_map_for_analysis[item]

def cal(data,var,cal):
    var_list = []
    for item in data:
        var_list.append(data[item][var])
    return(cal(var_list))

# 1. Descriptive
# Table 3.1
print('The record number in All is ' + str(len(metadata_map_for_analysis)))
print('The record number in SFH is ' + str(len(metadata_map_for_analysis_sfh)))
print('The record number in Townhous is ' + str(len(metadata_map_for_analysis_townhouse)))
print('The record number in Condo is ' + str(len(metadata_map_for_analysis_condo)))

print('the mean price per sqft for All is '+ str(round(cal(metadata_map_for_analysis,'price_per_sqft',np.mean),2)))
print('the mean price per sqft for SFH is ' + str(round(cal(metadata_map_for_analysis_sfh,'price_per_sqft',np.mean),2)))
print('the mean price per sqft for Townhouse is ' + str(round(cal(metadata_map_for_analysis_townhouse,'price_per_sqft',np.mean),2)))
print('the mean price per sqft for Condo is ' + str(round(cal(metadata_map_for_analysis_condo,'price_per_sqft',np.mean),2)))

print('the median price per sqft for All is '+ str(round(cal(metadata_map_for_analysis,'price_per_sqft',np.median),2)))
print('the median price per sqft for SFH is ' + str(round(cal(metadata_map_for_analysis_sfh,'price_per_sqft',np.median),2)))
print('the median price per sqft for Townhouse is ' + str(round(cal(metadata_map_for_analysis_townhouse,'price_per_sqft',np.median),2)))
print('the median price per sqft for Condo is ' + str(round(cal(metadata_map_for_analysis_condo,'price_per_sqft',np.median),2)))

print('the std price per sqft for All is '+ str(round(cal(metadata_map_for_analysis,'price_per_sqft',np.std),2)))
print('the std price per sqft for SFH is ' + str(round(cal(metadata_map_for_analysis_sfh,'price_per_sqft',np.std),2)))
print('the std price per sqft for Townhouse is ' + str(round(cal(metadata_map_for_analysis_townhouse,'price_per_sqft',np.std),2)))
print('the std price per sqft for Condo is ' + str(round(cal(metadata_map_for_analysis_condo,'price_per_sqft',np.std),2)))

#Histgram: check the distribution of price_per_sqft, sale_price, sqft by style
def dist_var(data, var):
    dist_var = []
    for item in data:
        dist_var.append(data[item][var])
    return dist_var

def check_dist(dist_var,style,loc):
    plb.subplot(2,2,loc)
    plb.hist(dist_var,color='orange', bins=24)
    plb.title(style)
    plb.xlabel("Price per sqft")
    plb.xlim([0,1400])
    plb.ylabel("Frequency")
    plb.grid(True)
    plb.show()
    plb.pause(3)


fig=plb.figure('Price per sqft Distribution',figsize=(10,6), dpi=120)
check_dist(dist_var(metadata_map_for_analysis, 'price_per_sqft'),'All',1)
check_dist(dist_var(metadata_map_for_analysis_sfh, 'price_per_sqft'),'SFH',2)
check_dist(dist_var(metadata_map_for_analysis_townhouse, 'price_per_sqft'),'Townhouse',3)
check_dist(dist_var(metadata_map_for_analysis_condo, 'price_per_sqft'),'Condo',4)
fig.autofmt_xdate()

# 2. Time series:
# Table data records counts/price for different property style
def time_serious_data_count(data):
    years = {}
    for item in data:
        year = data[item]['year']
        years[year] = years.get(year, 0) + 1
    return years

def time_serious_price_mean(data):
    price_map = {}
    year = ['2013','2014','2015','2016','2017']
    for yr in year:
        price = []
        for item in data:
            if data[item]['year'] == yr:
                price.append(data[item]['price_per_sqft'])
        price_map[yr]=round(np.mean(price),2)
    return price_map

print('Data record in All ' + str(time_serious_data_count(metadata_map_for_analysis)))
print('Data record in SFH ' + str(time_serious_data_count(metadata_map_for_analysis_sfh)))
print('Data record in Townhouse ' + str(time_serious_data_count(metadata_map_for_analysis_townhouse)))
print('Data record in Condo ' + str(time_serious_data_count(metadata_map_for_analysis_condo)))

print('the price for All is '+ str(time_serious_price_mean(metadata_map_for_analysis)))
print('the price for SFH is '+ str(time_serious_price_mean(metadata_map_for_analysis_sfh)))
print('the price for Townhouse is '+ str(time_serious_price_mean(metadata_map_for_analysis_townhouse)))
print('the price for Condo is '+ str(time_serious_price_mean(metadata_map_for_analysis_condo)))

#Question 1: Overall House price per square feet from 2013-2017

#aggregate data point in year month level
def agg_data_month_year(data_in):
    year_month_map = var_check(data_in, 'year_month')
    metadata_map_year_month = {}
    for ym in year_month_map:
        metadata_map_year_month_prep = {}
        house_price = []
        for item in data_in:
            if data_in[item]['year_month'] == ym:
                house_price.append(data_in[item]['price_per_sqft'])
        price_mean = np.mean(house_price)
        metadata_map_year_month_prep['price_per_sqft'] = price_mean
        metadata_map_year_month[ym]= metadata_map_year_month_prep
    return metadata_map_year_month

#aggregate data point in year month level for 3 styles
metadata_map_year_month=agg_data_month_year(metadata_map_for_analysis)
metadata_map_year_month_sfh = agg_data_month_year(metadata_map_for_analysis_sfh)
metadata_map_year_month_townhouse = agg_data_month_year(metadata_map_for_analysis_townhouse)
metadata_map_year_month_condo = agg_data_month_year(metadata_map_for_analysis_condo)

#price per sqft change from 2013 - 2017 for different property type
def year_month_dist(data,style,loc):
    x = []
    y = []
    for var in data:
        x.append((int(var[3])-3)*12+int(var[5:]))
        #x.append(var[2:])
        y.append(data[var]['price_per_sqft'])

    t_calculate = np.linspace(min(x),max(x),100)

    #we build the 'linear' interpolation function
    linear_i = interp1d(x, y)
    linear = linear_i(t_calculate)

    #this is a 'nearest' interpolation is obtained
    near_i=interp1d(x,y,kind='nearest')
    near = near_i(t_calculate)

    #this is a 'zero' interpolation is obtained
    zero_i = interp1d(x,y,kind='zero')
    zero=zero_i(t_calculate)

    #Now plot
    plb.subplot(2,2,loc)
    plb.plot(x, y, 'x', ms=5, label = ' data points')
    plb.plot(t_calculate,linear, label = ' linear interpolation')
    plb.plot(t_calculate,near,label = ' nearest interpolation')
    plb.plot(t_calculate,zero,label = ' zero interpolation')

    plb.title(style)
    plb.xlabel("Year-Month")
    plb.ylabel("Average Sale Price per sqft")
    plb.grid(True)
    plb.legend(loc='lower right')
    plb.ylim([0,800])

    plb.xticks([1, 4, 7, 10,
                13, 16, 19, 22,
                25, 28, 31, 34,
                37, 40, 43, 46,
                49, 52, 55, 58, 60],
               ['$13-01$','$13-04$','$13-07$','$13-10$',
                '$14-01$','$14-04$','$14-07$','$14-10$',
                '$15-01$','$15-04$','$15-07$','$15-10$',
                '$16-01$','$16-04$','$16-07$','$16-10$',
                '$17-01$','$17-04$','$17-07$','$17-10$', '$17-12$'])
    plb.show()
    plb.pause(2)

fig=plb.figure('Price per sqft 2013-2017',figsize=(10,6), dpi=120)
year_month_dist(metadata_map_year_month,'ALL',1)
year_month_dist(metadata_map_year_month_sfh,'SFH',2)
year_month_dist(metadata_map_year_month_townhouse,'Townhouse',3)
year_month_dist(metadata_map_year_month_condo,'Condo',4)
fig.autofmt_xdate()

# Put all property type into one figure, using data points method
def year_month_dist_for4(data,style):
    x = []
    y = []
    for var in data:
        x.append((int(var[3])-3)*12+int(var[5:]))
        y.append(data[var]['price_per_sqft'])

    plb.plot(x, y, ms=5, label = style)
    plb.title("Price per sqft for Different Property Types 2013-2017")
    plb.xlabel("Year-Month")
    plb.ylabel("Average Sale Price per sqft")
    plb.grid(True)
    plb.legend(loc='lower right')
    plb.ylim([0,800])

    plb.xticks([1, 4, 7, 10,
                13, 16, 19, 22,
                25, 28, 31, 34,
                37, 40, 43, 46,
                49, 52, 55, 58, 60],
               ['$Jan 2013$','$Apr 2013$','$Jul 2013$','$Oct 2013$',
                '$Jan 2014$','$Apr 2014$','$Jul 2014$','$Oct 2014$',
                '$Jan 2015$','$Apr 2015$','$Jul 2015$','$Oct 2015$',
                '$Jan 2016$','$Apr 2016$','$Jul 2016$','$Oct 2016$',
                '$Jan 2017$','$Apr 2017$','$Jul 2017$','$Oct 2017$',
                '$Dec 2017$'])


fig = plb.figure('Price per sqft for Different Property Types 2013-2017',figsize=(10,6), dpi=120)
year_month_dist_for4(metadata_map_year_month,'ALL')
year_month_dist_for4(metadata_map_year_month_sfh,'SFH')
year_month_dist_for4(metadata_map_year_month_townhouse,'Townhouse')
year_month_dist_for4(metadata_map_year_month_condo,'Condo')
fig.autofmt_xdate()

###Spatial

def get_points2d(data,style,loc):
    Latitude = []
    Longitude = []
    for item in data:
        Latitude.append(data[item]["lat"])
        Longitude.append(data[item]["lon"])

    plb.subplot(2,2,loc)
    plb.plot(Longitude, Latitude, 'x', ms=5, label='data points', alpha=0.3)
    plb.title(style)
    plb.xlabel('Longitude')
    plb.ylabel('Latitude')
    plb.grid()
    plb.show()
    plb.pause(2)

fig = plt.figure('2D Data Points Location',figsize=(10,6), dpi=120)
get_points2d(metadata_map_for_analysis,'ALL',1)
get_points2d(metadata_map_for_analysis_sfh, 'SFH',2)
get_points2d(metadata_map_for_analysis_townhouse, 'Townhouse',3)
get_points2d(metadata_map_for_analysis_condo, 'Condo',4)
fig.autofmt_xdate()

def new_geo_group_func(data):
    #get the lat and lon
    Latitude = []
    Longitude = []
    for item in data:
        Latitude.append(data[item]["lat"])
        Longitude.append(data[item]["lon"])
    #add new lat/lon group
    new_geo_group = {}
    for item in data:
        new_geo_group[item] = data[item]
        new_geo_group[item]["group_lat"] = int((data[item]["lat"]-np.min(Latitude))/0.01)
        new_geo_group[item]["group_lon"] = int((data[item]["lon"] - np.min(Longitude)) / 0.01)
        new_geo_group[item]["group"] = str(data[item]["year"]) + '-' + \
                                       str(int((data[item]["lat"]-np.min(Latitude))/0.01)) + \
                                       "-"+ str(int((data[item]["lon"] - np.min(Longitude)) / 0.01))

    group_map = var_check(new_geo_group, 'group')
    metadata_map_new_geo = {}
    for group in group_map:
        metadata_map_new_geo_prep = {}
        house_price = []
        latitude = []
        longitude = []
        for item in new_geo_group:
            if new_geo_group[item]['group'] == group:
                house_price.append(new_geo_group[item]['price_per_sqft'])
                latitude.append(new_geo_group[item]['lat'])
                longitude.append(new_geo_group[item]['lon'])
        price_mean = np.mean(house_price)
        lat_mean = np.mean(latitude)
        lon_mean = np.mean(longitude)
        metadata_map_new_geo_prep['price_per_sqft'] = price_mean
        metadata_map_new_geo_prep['lat'] = lat_mean
        metadata_map_new_geo_prep['lon'] = lon_mean
        metadata_map_new_geo[group]= metadata_map_new_geo_prep
        metadata_map_new_geo[group]['year']= group[:4]
        metadata_map_new_geo[group]['group'] = group
        metadata_map_new_geo[group]['geo_group'] = group[5:]
    return metadata_map_new_geo


def get_points3d_price(data, style):
    Latitude = []
    Longitude = []
    Depth = []
    for item in data:
        Latitude.append(data[item]["lat"])
        Longitude.append(data[item]["lon"])
        Depth.append(data[item]["price_per_sqft"])

    fig = plt.figure('3D Data Location ' + style, figsize=(10,6), dpi=120)
    ax = plt.axes(projection='3d')
    x = Longitude,
    y = Latitude
    z = Depth
    ax.scatter3D(x, y, z, c=z, cmap='gist_earth')
    ax.set_title('3D Data Location ' + style)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Price per sqft')

    plt.show()
    fig.autofmt_xdate()
    plb.pause(2)

get_points3d_price(metadata_map_for_analysis,'All')
get_points3d_price(metadata_map_for_analysis_sfh,'SFH')
get_points3d_price(metadata_map_for_analysis_townhouse,'Townhouse')
get_points3d_price(metadata_map_for_analysis_condo,'Condo')

get_points3d_price(new_geo_group_func(metadata_map_for_analysis),'All Methods: average')
get_points3d_price(new_geo_group_func(metadata_map_for_analysis_sfh),'SFH  Methods: average')
get_points3d_price(new_geo_group_func(metadata_map_for_analysis_townhouse),'Townhouse  Methods: average')
get_points3d_price(new_geo_group_func(metadata_map_for_analysis_condo),'Condo  Methods: average')

#price geographically

def plot2d_price(data,yr,style,loc):
    # grid the data.
    Latitude=[]
    Longitude=[]
    Depth=[]

    for item in data:
        if data[item]["year"] in yr:
            Latitude.append(data[item]["lat"])
            Longitude.append(data[item]["lon"])
            Depth.append(data[item]["price_per_sqft"])

    plb.subplot(2,2,loc)
    X = np.asarray(Longitude)
    Y = np.asarray(Latitude)
    Z = np.asarray(Depth)
    xi = np.linspace(min(X), max(X), (len(Z)/3))
    yi = np.linspace(min(Y), max(Y), (len(Z)/3))
    zi = griddata((X,Y), Z, (xi[None,:], yi[:,None]), method='nearest')
    CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
    CS = plt.contourf(xi, yi, zi, 15, cmap='gist_earth')
    plt.colorbar() # draw colorbar
    plt.scatter(X,Y,marker='o',c='black',s=5, alpha=0.3)
    plb.title(style)
    plb.xlabel("Latitude")
    plb.ylabel("Longitude")
    plt.show()
    plb.pause(2)

fig = plt.figure('2D Price per sqft', figsize=(10,6), dpi=120)
plot2d_price(new_geo_group_func(metadata_map_for_analysis),{'2017','2016','2015','2014','2013'},'ALL',1)
plot2d_price(new_geo_group_func(metadata_map_for_analysis_sfh),{'2017','2016','2015','2014','2013'},'SFH',2)
plot2d_price(new_geo_group_func(metadata_map_for_analysis_townhouse),{'2017','2016','2015','2014','2013'},'Townhouse',3)
plot2d_price(new_geo_group_func(metadata_map_for_analysis_condo),{'2017','2016','2015','2014','2013'},'Condo',4)
fig.autofmt_xdate()

#price change from 2013 to 2017 for different geo-group
def geo_change_func(data):

    agg_data = new_geo_group_func(data)
    group_map = var_check(agg_data, 'geo_group')
    geo_change = {}

    for geo_group in group_map:
        geo_change_prep = {}
        price_2013, price_2017 = None, None
        for item in agg_data:
            if agg_data[item]['geo_group'] == geo_group and agg_data[item]['year'] in {'2013'}:
                price_2013 = agg_data[item]['price_per_sqft']
                lat_2013 = agg_data[item]['lat']
                lon_2013 = agg_data[item]['lon']
            if agg_data[item]['geo_group'] == geo_group and agg_data[item]['year'] in {'2017'}:
                price_2017 = agg_data[item]['price_per_sqft']
                lat_2017 = agg_data[item]['lat']
                lon_2017 = agg_data[item]['lon']
        if price_2013 is not None and price_2017 is not None:
            price_perc = round((price_2017-price_2013)/price_2013*100,2)
            lat_mean = (lat_2013+lat_2017)/2
            lon_mean = (lon_2013+lon_2017)/2
            geo_change_prep['price_perc'] = price_perc
            geo_change_prep['lat'] = lat_mean
            geo_change_prep['lon'] = lon_mean
            geo_change[geo_group]= geo_change_prep
            geo_change[geo_group]['year'] = '2013-2017'
    return geo_change


def plot2d_price_perc(data,yr,style,loc):
    # grid the data.
    Latitude=[]
    Longitude=[]
    Depth=[]

    for item in data:
        if data[item]["year"] in yr:
            Latitude.append(data[item]["lat"])
            Longitude.append(data[item]["lon"])
            Depth.append(data[item]["price_perc"])

    plb.subplot(2,2,loc)
    X = np.asarray(Longitude)
    Y = np.asarray(Latitude)
    Z = np.asarray(Depth)
    xi = np.linspace(min(X), max(X), (len(Z)/3))
    yi = np.linspace(min(Y), max(Y), (len(Z)/3))
    zi = griddata((X,Y), Z, (xi[None,:], yi[:,None]), method='nearest')
    CS = plt.contour(xi,yi,zi,15,linewidths=0.5,colors='k')
    CS = plt.contourf(xi, yi, zi, 15, cmap='gist_earth')
    plt.colorbar() # draw colorbar
    plt.scatter(X,Y,marker='o',c='black',s=5, alpha=0.7)
    plb.title(style)
    plb.xlabel("Latitude")
    plb.ylabel("Longitude")
    plt.show()
    plb.pause(1)

fig = plt.figure('2D Price Increase Percentage 2013 - 2017', figsize=(10,6), dpi=120)
plot2d_price_perc(geo_change_func(metadata_map_for_analysis),{'2013-2017'}, 'ALL', 1)
plot2d_price_perc(geo_change_func(metadata_map_for_analysis_sfh),{'2013-2017'},'SFH',2)
plot2d_price_perc(geo_change_func(metadata_map_for_analysis_townhouse),{'2013-2017'},'Townhouse',3)
plot2d_price_perc(geo_change_func(metadata_map_for_analysis_condo),{'2013-2017'},'Condo',4)
fig.autofmt_xdate()

def plot3d_price_perc(data,style):
    Latitude = []
    Longitude = []
    Depth = []
    for item in data:
        Latitude.append(data[item]["lat"])
        Longitude.append(data[item]["lon"])
        Depth.append(data[item]["price_perc"])

    fig = plt.figure('3D Price Increase Percentage 2013 - 2017 ' + style, figsize=(10,6), dpi=120)
    ax = plt.axes(projection='3d')
    x = Longitude,
    y = Latitude
    z = Depth
    ax.scatter3D(x, y, z, c=z, cmap='gist_earth')
    ax.set_title('Data Points Location')
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_zlabel('Price Change Percentage')
    ax.set_title("3D Price Increase Percentage 2013 - 2017 " + style)
    fig.autofmt_xdate()
    plt.show()
    plb.pause(3)

plot3d_price_perc(geo_change_func(metadata_map_for_analysis),'All')
plot3d_price_perc(geo_change_func(metadata_map_for_analysis_sfh),'SFH')
plot3d_price_perc(geo_change_func(metadata_map_for_analysis_townhouse),'Townhouse')
plot3d_price_perc(geo_change_func(metadata_map_for_analysis_condo),'Condo')



