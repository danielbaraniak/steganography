from PySide6.QtWidgets import QWidget, QGridLayout, QLabel

class MetricsWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QGridLayout()

        self.loading_indicator = QLabel("Computing metrics...")
        self.loading_indicator.hide()

        # Descriptive labels
        self.mseDescLabel = QLabel("MSE:")
        self.psnrDescLabel = QLabel("PSNR:")
        self.ssimDescLabel = QLabel("SSIM:")
        self.img1MinDescLabel = QLabel("Image 1 - Min:")
        self.img1MaxDescLabel = QLabel("Image 1 - Max:")
        self.img1StdDescLabel = QLabel("Image 1 - Std:")
        self.img2MinDescLabel = QLabel("Image 2 - Min:")
        self.img2MaxDescLabel = QLabel("Image 2 - Max:")
        self.img2StdDescLabel = QLabel("Image 2 - Std:")
        self.diffMinDescLabel = QLabel("Difference - Min:")
        self.diffMaxDescLabel = QLabel("Difference - Max:")
        self.diffStdDescLabel = QLabel("Difference - Std:")

        # Data labels
        self.mseLabel = QLabel()
        self.psnrLabel = QLabel()
        self.ssimLabel = QLabel()
        self.img1MinLabel = QLabel()
        self.img1MaxLabel = QLabel()
        self.img1StdLabel = QLabel()
        self.img2MinLabel = QLabel()
        self.img2MaxLabel = QLabel()
        self.img2StdLabel = QLabel()
        self.diffMinLabel = QLabel()
        self.diffMaxLabel = QLabel()
        self.diffStdLabel = QLabel()

        labels = [
            (self.mseDescLabel, self.mseLabel),
            (self.psnrDescLabel, self.psnrLabel),
            (self.ssimDescLabel, self.ssimLabel),
            (self.img1MinDescLabel, self.img1MinLabel),
            (self.img1MaxDescLabel, self.img1MaxLabel),
            (self.img1StdDescLabel, self.img1StdLabel),
            (self.img2MinDescLabel, self.img2MinLabel),
            (self.img2MaxDescLabel, self.img2MaxLabel),
            (self.img2StdDescLabel, self.img2StdLabel),
            (self.diffMinDescLabel, self.diffMinLabel),
            (self.diffMaxDescLabel, self.diffMaxLabel),
            (self.diffStdDescLabel, self.diffStdLabel),
        ]

        self.layout.addWidget(self.loading_indicator, 0, 0, 1, 2)
        for idx, (desc, label) in enumerate(labels):
            idx += 1
            self.layout.addWidget(desc, idx, 0)
            self.layout.addWidget(label, idx, 1)

        self.setLayout(self.layout)

    def set_metrics(self, stats):
        self.loading_indicator.hide()
        self.mseLabel.setText(str(stats['diff']['mse']))
        self.psnrLabel.setText(str(stats['diff']['psnr']))
        self.ssimLabel.setText(str(stats['diff']['ssim']))
        self.img1MinLabel.setText(str(stats['img1']['min']))
        self.img1MaxLabel.setText(str(stats['img1']['max']))
        self.img1StdLabel.setText(str(stats['img1']['std']))
        self.img2MinLabel.setText(str(stats['img2']['min']))
        self.img2MaxLabel.setText(str(stats['img2']['max']))
        self.img2StdLabel.setText(str(stats['img2']['std']))
        self.diffMinLabel.setText(str(stats['diff']['min']))
        self.diffMaxLabel.setText(str(stats['diff']['max']))
        self.diffStdLabel.setText(str(stats['diff']['std']))
