for f in data/50Ohm_FrontPanelTest_20210811/*csv
do
    fname=${f}
    echo "$f"
    python3 main.py $fname
done

echo "Analysis complete!"