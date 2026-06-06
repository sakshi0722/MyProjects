import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory

IMG_SIZE = (224, 224)
BATCH = 16

print("Loading dataset...")

train_ds = image_dataset_from_directory(
    "dataset",
    image_size=IMG_SIZE,
    batch_size=BATCH
)

class_names = train_ds.class_names
print("Classes found:", class_names)

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224,224,3),
    include_top=False,
    weights="imagenet"
)

base_model.trainable = False

x = tf.keras.layers.GlobalAveragePooling2D()(base_model.output)
output = tf.keras.layers.Dense(len(class_names), activation="softmax")(x)

model = tf.keras.Model(base_model.input, output)

model.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"]
)

print("Training started...")

model.fit(train_ds, epochs=5)

model.save("injury_model.h5")

print("Model saved successfully as injury_model.h5")