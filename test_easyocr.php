<?php
if (isset($_FILES['image']) && !empty($_FILES['image'])) {
    $image = $_FILES['image'];
    // 192.168.1.2:5000
    // 192.168.16.103
    $url = 'http://192.168.16.105:5000/process';
    $postData = array('image' => new CURLFile($image['tmp_name']));

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    curl_close($ch);
    $tieude = "";
    $ngay = "";
    $noigui = "";
    $soqd = "";
    $trichyeu = "";
    $results = json_decode($response, true);
    if ($results) {
        foreach ($results as $result) {
            $class_name = $result['class'];
            $text = $result['text'];
            if ($class_name === 'tieude') {
                $tieude .= ($tieude !== "" ? ", " : "") . $text;
            } elseif ($class_name === 'ngay') {
                $ngay .= ($ngay !== "" ? ", " : "") . $text;
            } elseif ($class_name === 'noigui') {
                $noigui .= ($noigui !== "" ? ", " : "") . $text;
            } elseif ($class_name === 'soqd') {
                $soqd .= ($soqd !== "" ? ", " : "") . $text;
            } elseif ($class_name === 'trichyeu') {
                $trichyeu .= ($trichyeu !== "" ? ", " : "") . $text;
            }
        }
    } else {
        echo "Không có kết quả.";
    }
}

?>

<!DOCTYPE html>
<html>

<head>
    <title>Text Extraction with EasyOCR</title>
</head>

<body>
    <h1>Text Extraction with EasyOCR</h1>
    <form action="" method="POST" enctype="multipart/form-data">
        <input type="file" name="image" accept="image/*">
        <button type="submit">Extract Text</button>
    </form>
    <?php if (isset($noigui) && $noigui !== ""): ?>
        <h2>noigui:</h2>
        <input type="text" value="<?php echo $noigui; ?>" style="width: 50%;">
    <?php endif; ?>
    <?php if (isset($soqd) && $soqd !== ""): ?>
        <h2>soqd:</h2>
        <input type="text" value="<?php echo $soqd; ?>" style="width: 50%;">
    <?php endif; ?>
    <?php if (isset($ngay) && $ngay !== ""): ?>
        <h2>ngay:</h2>
        <input type="text" value="<?php echo $ngay; ?>" style="width: 50%;">
    <?php endif; ?>
    <?php if (isset($tieude) && $tieude !== ""): ?>
        <h2>Tieude:</h2>
        <textarea rows="10" cols="100"><?php echo $tieude; ?></textarea>
    <?php endif; ?>


</body>

</html>