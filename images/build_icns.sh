mkdir cat_scream_emoji.iconset
sips -z 16 16     cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_16x16.png
sips -z 32 32     cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_16x16@2x.png
sips -z 32 32     cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_32x32.png
sips -z 64 64     cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_32x32@2x.png
sips -z 128 128   cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_128x128.png
sips -z 256 256   cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_128x128@2x.png
sips -z 256 256   cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_256x256.png
sips -z 512 512   cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_256x256@2x.png
sips -z 512 512   cat_scream_emoji.png --out cat_scream_emoji.iconset/icon_512x512.png
cp cat_scream_emoji.png cat_scream_emoji.iconset/icon_512x512@2x.png
iconutil -c icns cat_scream_emoji.iconset
rm -R cat_scream_emoji.iconset