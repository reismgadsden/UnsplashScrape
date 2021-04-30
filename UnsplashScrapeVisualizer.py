import UnsplashScrape
import datetime
import matplotlib.ticker as mtick
import numpy as np
import matplotlib.pyplot as plt
import webbrowser
import warnings
import pandas as pd


def top_photographer(df):
    df = df[df.photographer != "ballparkbrand"]
    new_df = df.groupby(by=["photographer"], as_index=False)["views"].sum()
    new_df = new_df.sort_values(by=["views"], ascending=False, na_position='last')
    new_df = new_df.head(10)
    fig, ax = plt.subplots()
    plt.title("Top 10 Photographers by Views on " + datetime.date.today().strftime("%B %d, %Y"))
    plt.xlabel("Photographer")
    plt.ylabel("Views")
    ax.bar(new_df["photographer"].tolist(), new_df["views"], width=0.5, align="center", color='r')
    ymin, ymax = ax.get_ylim()
    ax.yaxis.set_ticks(np.arange(0, ymax+1000000, 1000000.0))
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.0e"))
    ax.xaxis.set_ticks(new_df["photographer"])
    ax.set_xticklabels(new_df["photographer"], ha='right', rotation=45)

    for tick in ax.xaxis.get_minor_ticks():
        tick.tick1line.set_markersize(0)
        tick.tick2line.set_markersize(0)
        tick.label1.set_horizontalalignment('center')
    fig.savefig("data/top_photographers.png", bbox_inches="tight")

def avg_make_model(df):
    df = df[df['camera_make'].notna()]
    df = df[df['camera_model'].notna()]
    new_df = df.groupby(['camera_make', 'camera_model'])["views", "downloads", "count"]\
        .apply(lambda x : x.astype(int).sum()).reset_index()
    new_df['views'] = np.where(new_df['count'] < 1, new_df['count'], new_df['views'] / new_df['count'])
    new_df['downloads'] = np.where(new_df['count'] < 1, new_df['count'], new_df['downloads'] / new_df['count'])
    camera_makes = new_df.camera_make.unique()
    i = 0
    for make in camera_makes:
        fig, ax = plt.subplots(2)
        fig.tight_layout()
        fig.subplots_adjust(hspace=1.0)
        make_df = new_df[new_df['camera_make'] == make]
        ax[0].bar(make_df['camera_model'], make_df['views'], width=0.1, align='center', color='b')
        ax[0].set_xticklabels(make_df['camera_model'], ha='right', rotation=45)
        ax[0].set_ylim(0, make_df["views"].max()+100)
        ax[0].yaxis.set_ticks([0, round(((make_df["views"].max() + (make_df["views"].max() / 10)) / 2)),
                                  make_df["views"].max() + (make_df["views"].max() / 10)])
        ax[0].yaxis.set_major_formatter(mtick.FormatStrFormatter("%.0e"))

        ax[1].bar(make_df['camera_model'], make_df['downloads'], width=0.1, align='center', color='r')
        ax[1].set_xticklabels(make_df['camera_model'], ha='right', rotation=45)
        ax[1].set_ylim(0, make_df["downloads"].max() + 100)
        ax[1].yaxis.set_ticks([0, round(((make_df["downloads"].max() + (make_df["downloads"].max() / 10)) / 2)),
                                  make_df["downloads"].max() + (make_df["downloads"].max() / 10)])

        ax[0].set_ylabel("Views")
        ax[1].set_ylabel("Downloads")
        ax[0].set_title("Total Views and Downloads for " + make + " cameras on " + datetime.date.today().strftime("%B %d, %Y") + "\n")
        fig.savefig("data/" + make + "_avg_views_dls.png", bbox_inches="tight")
        i += 1


def most_used_qual(df):
    df = df[df['camera_make'].notna()]
    df = df[df['camera_model'].notna()]

    focal_len_df = df[df['focal_len'].notna()]
    aperture_df = df[df['aperture'].notna()]
    shutter_speed_df = df[df['shutter_speed'].notna()]
    iso_df = df[df['iso'].notna()]

    focal_len_df = focal_len_df.groupby(["focal_len"])['count'].apply(lambda x : x.astype(float).sum()).reset_index().sort_values(['focal_len'], ascending=False)
    aperture_df = aperture_df.groupby(["aperture"])['count'].apply(lambda x : x.astype(float).sum()).reset_index().sort_values(['aperture'], ascending=False)
    shutter_speed_df = shutter_speed_df.groupby(["shutter_speed"])['count'].apply(lambda x : x.astype(float).sum()).reset_index().sort_values(['shutter_speed'], ascending=False)
    iso_df = iso_df.groupby(["iso"])['count'].apply(lambda x : x.astype(int).sum()).reset_index().sort_values(['iso'], ascending=False)

    fig, ax = plt.subplots(4)
    fig.tight_layout()
    fig.subplots_adjust(hspace=1.0)
    ax[0].plot(focal_len_df['focal_len'], focal_len_df['count'], color='y')
    ax[0].set_xlabel("Focal Length (millimeters)")

    ax[1].plot(aperture_df['aperture'], aperture_df['count'], color='r')
    ax[1].set_xlabel("Aperture (\u0192/n)")

    ax[2].plot(shutter_speed_df['shutter_speed'], shutter_speed_df['count'], color='g')
    ax[2].set_xlabel("Shutter Speed (seconds)")
    ax[2].set_xscale('log')

    ax[3].plot(iso_df['iso'], iso_df['count'], color='b')
    ax[3].set_xlabel("ISO")

    ax[0].set_title("Most used camera settings as of " + datetime.date.today().strftime("%B %d, %Y"))
    fig.savefig("data/camera_settings.png", bbox_inches="tight")


def most_pop_img(df):
    df.sort_values(['views'], ascending=False)
    webbrowser.open_new_tab(df['img_page'].iloc[0])


def perf_cam(df):
    make_model_df = df[df['camera_make'].notna()]
    make_model_df = make_model_df[make_model_df['camera_model'].notna()]
    focal_len_df = df[df['focal_len'].notna()]
    aperture_df = df[df['aperture'].notna()]
    shutter_speed_df = df[df['shutter_speed'].notna()]
    iso_df = df[df['iso'].notna()]

    make_model_df = df.groupby(['camera_make', 'camera_model'])["views", "count"] \
        .apply(lambda x: x.astype(int).sum()).reset_index()
    make_model_df['views'] = np.where(make_model_df['count'] < 1, make_model_df['count'], make_model_df['views'] / make_model_df['count'])
    make_model_df = make_model_df.sort_values(['views'], ascending=False)
    perf_make = make_model_df['camera_make'].iloc[0]
    perf_model = make_model_df['camera_model'].iloc[0]

    focal_len_df = focal_len_df.groupby(["focal_len"])['views', 'count'].apply(
        lambda x: x.astype(float).sum()).reset_index()
    focal_len_df['views'] = np.where(focal_len_df['count'] < 1, focal_len_df['count'],
                                     focal_len_df['views'] / focal_len_df['count'])
    focal_len_df = focal_len_df.sort_values(['views'], ascending=False)
    perf_focal_len = focal_len_df['focal_len'].iloc[0]

    aperture_df = aperture_df.groupby(["aperture"])['views', 'count'].apply(lambda x: x.astype(float).sum())\
        .reset_index()
    aperture_df['views'] = np.where(aperture_df['count'] < 1, aperture_df['count'],
                                     aperture_df['views'] / aperture_df['count'])
    aperture_df = aperture_df.sort_values(['views'], ascending=False)
    perf_aperture = aperture_df['aperture'].iloc[0]

    shutter_speed_df = shutter_speed_df.groupby(["shutter_speed"])['views', 'count'].apply(
        lambda x: x.astype(float).sum()).reset_index()
    shutter_speed_df['views'] = np.where(shutter_speed_df['count'] < 1, shutter_speed_df['count'],
                                    shutter_speed_df['views'] / shutter_speed_df['count'])
    shutter_speed_df = shutter_speed_df.sort_values(['views'], ascending=False)
    perf_shutter_speed = shutter_speed_df['shutter_speed'].iloc[0]

    iso_df = iso_df.groupby(["iso"])['views', 'count'].apply(lambda x: x.astype(int).sum()).reset_index()
    iso_df['views'] = np.where(iso_df['count'] < 1, iso_df['count'],
                                    iso_df['views'] / iso_df['count'])
    iso_df = iso_df.sort_values(['views'], ascending=False)
    perf_iso = iso_df['iso'].iloc[0]

    print("The perfect camera as of " + datetime.date.today().strftime("%B %d, %Y")+ "\n" +
          "Make: " + perf_make +
          "\nModel: " + perf_model +
          "\nFocal Length: " + str(perf_focal_len) + "mm" +
          "\nAperture: ƒ/" + str(perf_aperture) +
          "\nShutter Speed: " + str(perf_shutter_speed) + " seconds" +
          "\nISO: " + str(perf_iso) + "\n")


if __name__ == "__main__":
    warnings.simplefilter('ignore')
    print("Welcome to the Unsplash Scraper Visualizer")
    while True:
        use_csv = input("Would you like to start new scape or use a csv from the last scrape."
                        " (New scrape will take 30-45 mins to complete) Type 'csv' to load from csv, type 'new' to "
                        "start new scrape:" )
        if use_csv[0].lower() == 'c':
            df = pd.read_csv('data/data.csv')
            break
        elif use_csv[0].lower() == 'n':
            us = UnsplashScrape.UnsplashScrape("https://unsplash.com/", 1000)
            df = us.df
            break
        else:
            print("Invalid inout. Please try again.")

    while True:
        print("\nMenu")
        print("1. View Top 10 Photographers by Views on ")
        print("2. View Average Downloads and Views by Camera Make and Model")
        print("3. View Most Used Camera Settings")
        print("4. View the Most Viewed Image")
        print("5. Build the Perfect Camera")
        print("6. Exit\n")

        choice = input("Please make a menu selection: ").strip()

        if choice == "1":
            top_photographer(df)
        elif choice == "2":
            avg_make_model(df)
        elif choice == "3":
            most_used_qual(df)
        elif choice == "4":
            most_pop_img(df)
        elif choice == "5":
            perf_cam(df)
            input("Type anything to return to menu: ")
        elif choice == "6":
            print("Goodbye, thank you for using Unsplash Scrape Visualizer")
            break
        else:
            print("Invalid Menu Choice Please Enter Another Choice")