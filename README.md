# CLI版 位置偽装ツール

このプロジェクトは、AndroidおよびiOSデバイスの位置情報を偽装するためのPythonスクリプト群です。静的な位置設定と、2点間の移動シミュレーションの両方に対応しています。

## 主な機能

- **静的な位置設定:** デバイスのGPS情報を、指定した緯度経度に設定します。
- **移動シミュレーション:** 開始地点から目標地点まで、指定した速度で移動する様子をシミュレートします。
- **プラットフォーム対応:** Android（`adb`経由）およびiOS（`xcrun`経由のシミュレータ）に対応しています。
- **ログ記録:** すべての移動シミュレーションは、監査用にCSVファイルへ記録されます。
- **位置の復元:** 偽装を開始する前の元の位置を保存し、復元することができます。

## 事前準備

### 共通
- Python 3.12以上
- `haversine`ライブラリ (`pip install haversine`)

### Android向け
- Android SDK Platform-Toolsがインストールされ、`adb`コマンドへのパスが通っていること。
- 開発者モードとUSBデバッグが有効化されたAndroidデバイス。

### iOS向け
- XcodeおよびXcode Command Line ToolsがインストールされたmacOS。
- iOSシミュレータ（またはXcode 17以降で開発者モードが有効な物理デバイス）。

## 使い方

本ツールは、`android_tool.py`と`ios_tool.py`の2つの主要なスクリプトで構成されています。

### 共通コマンド

両方のツールで、同様のコマンド体系を共有しています。

- `set`: 静的な位置を設定します。
- `move`: 2点間の移動をシミュレートします。
- `save`: 現在の位置情報をファイルに保存します。
- `restore`: 保存したファイルから位置を復元します。

### Androidでの使用例

**1. 接続デバイスの確認:**
```bash
python android_tool.py
```
*(注意: この機能は、他のコマンドで対象デバイスを選択するために暗黙的に使用されます)*

**2. 静的な位置を設定する（例: 東京駅）:**
```bash
python android_tool.py set 35.681236 139.767125
```

**3. 東京駅から秋葉原駅まで、秒速5mで移動をシミュレートする:**
```bash
python android_tool.py move 35.681236 139.767125 35.69836 139.773098 --speed 5
```

**4. 位置偽装の前に、現在の位置を保存する:**
```bash
# 例えば、現在地が渋谷スクランブル交差点の場合
python android_tool.py save 35.65952 139.700475
```

**5. 元の位置に復元する:**
```bash
python android_tool.py restore
```

### iOSでの使用例

**1. シミュレータの静的な位置を設定する:**
```bash
# <YOUR_SIMULATOR_UDID> の部分は、お使いのシミュレータのUDIDに置き換えてください
python ios_tool.py set <YOUR_SIMULATOR_UDID> 34.052235 -118.243683
```

**2. シミュレータ上で移動をシミュレートする:**
```bash
python ios_tool.py move <YOUR_SIMULATOR_UDID> 34.052235 -118.243683 34.056235 -118.248683 --speed 3
```

**3. 位置の保存と復元（Androidと同様ですが、UDIDの指定が必要です）:**
```bash
python ios_tool.py save <YOUR_SIMULATOR_UDID> 34.052235 -118.243683
python ios_tool.py restore <YOUR_SIMULATOR_UDID>
```

## ログ機能

`move`コマンドが実行されるたびに、`teleport_log_{タイムスタンプ}_{デバイスID}.csv`という名前のログファイルが同じディレクトリに作成されます。このファイルには、シミュレーションの各ステップにおけるタイムスタンプと座標が記録されます。