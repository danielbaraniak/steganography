from PySide6.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout


class MetricsWidget(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()

        self.loading_indicator = QLabel("Computing metrics...")
        self.loading_indicator.hide()

        self.metrics_individual = [
            ("Min:", "min"),
            ("Max:", "max"),
            ("Shape:", "shape"),
        ]
        self.labels_individual = [
            (QLabel(desc_text), QLabel(), QLabel())
            for desc_text, _ in self.metrics_individual
        ]

        self.metrics_common = [
            ("MSE:", "mse"),
            ("PSNR:", "psnr"),
            ("SSIM:", "ssim"),
        ]
        self.labels_common = [
            (QLabel(desc_text), QLabel()) for desc_text, _ in self.metrics_common
        ]

        main_layout.addWidget(self.loading_indicator)
        main_layout.addLayout(
            self.create_grid(self.metrics_individual, self.labels_individual)
        )
        main_layout.addLayout(self.create_grid(self.metrics_common, self.labels_common))
        self.setLayout(main_layout)

    def create_grid(self, metrics, labels):
        grid_layout = QGridLayout()

        for idx, ((desc_text, _), labels) in enumerate(zip(metrics, labels)):
            for i, label in enumerate(labels):
                grid_layout.addWidget(label, idx, i)

        return grid_layout

    def set_metrics(self, stats):
        self.loading_indicator.hide()

        for (_, key), (_, label_img1, label_img2) in zip(
            self.metrics_individual, self.labels_individual
        ):
            label_img1.setText(str(stats["img1"][key]))
            label_img2.setText(str(stats["img2"][key]))

        for (_, key), (_, val) in zip(self.metrics_common, self.labels_common):
            val.setText(str(stats["diff"][key]))
