


# ==========================================
# 3. TENSORFLOW DATA PIPELINE - UPDATED
# ==========================================
def process_path(file_path, irradiance):
    # Read the physical file
    img = tf.io.read_file(file_path)
    # Decode JPEG to a tensor
    img = tf.image.decode_jpeg(img, channels=3)
    # Resize to EfficientNetB4 specs (380x380)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    
    return img, irradiance

def create_tf_dataset(file_paths, targets):
    # 🚨 FIX 3: Cast dataset inputs to tf.string and tf.float32 explicitly
    dataset = tf.data.Dataset.from_tensor_slices((
        tf.cast(file_paths, tf.string),
        tf.cast(targets, tf.float32)
    ))
    
    dataset = dataset.map(process_path, num_parallel_calls=tf.data.AUTOTUNE)
    dataset = dataset.shuffle(buffer_size=1000)
    dataset = dataset.batch(BATCH_SIZE)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    
    return dataset