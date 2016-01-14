#!/bin/bash

echo "Running all scrapers..."
python -m scrapers.berniesanders_com.articles
python -m scrapers.berniesanders_com.issues
python -m scrapers.berniesanders_com.events
python -m scrapers.berniesanders_com.news
python -m scrapers.youtube_com.bernie_2016


echo "Done."
