import tensorflow.contrib.slim as slim
import sys
sys.path.append('../../')
import numpy as np
from scripts.non_rigid_transformer import *


def STNet(img, batch_size, image_size, num_class=8, dropout_keep_prob=0.7,
          stn_init=np.array([0.7, 0.0, -0.2, 0.0, 0.7, -0.2, 0.0, 0.0]).astype('float32'),
          scope='STN', is_training=False, reuse=None):
    outsize = (int(image_size), int(image_size))
    stl = ProjectiveTransformer(outsize)
    # initial = np.reshape(stn_init.flatten(), [1, stl.param_dim])
    # theta = tf.add(initial, 0.02 * tf.random_normal([batch_size, stl.param_dim]))
    with tf.variable_scope(scope, reuse=reuse):
        net = slim.conv2d(img, 32, [7, 7], stride=2, scope='conv1',
                          weights_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                          biases_initializer=tf.zeros_initializer())

        net = slim.max_pool2d(net, [2, 2], [2, 2], padding='VALID', scope='pool1')

        net = slim.conv2d(net, 64, [5, 5], stride=2, scope='conv2',
                          weights_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                          biases_initializer=tf.zeros_initializer())

        net = slim.max_pool2d(net, [2, 2], [2, 2], padding='VALID', scope='pool2')

        net = slim.conv2d(net, 128, [3, 3], stride=2, scope='conv3',
                          weights_initializer=tf.contrib.layers.xavier_initializer_conv2d(),
                          biases_initializer=tf.zeros_initializer())

        net = slim.max_pool2d(net, [2, 2], [2, 2], padding='VALID', scope='pool3')
        net = slim.fully_connected(tf.contrib.layers.flatten(net), 64, scope='fc_1', weights_initializer=tf.zeros_initializer(),
                                   biases_initializer=tf.zeros_initializer(), trainable=is_training)
        # net = slim.dropout(net, dropout_keep_prob, is_training=is_training, scope='fc_1_dropout')
        net = slim.fully_connected(net, num_class, scope='fc_2', weights_initializer=tf.zeros_initializer(),
                                   biases_initializer=tf.zeros_initializer(),trainable=False)
        net = tf.nn.bias_add(net, stn_init)
        # net = slim.dropout(net, dropout_keep_prob, is_training=is_training, scope='fc_2_dropout')
        outputs = tf.reshape(stl.transform(img, net), [batch_size, int(image_size), int(image_size), 3])

        return outputs


def STNet_arg_scope(weight_decay=0.00005,
                    batch_norm_decay=0.9997,
                    batch_norm_epsilon=0.001,
                    use_batch_norm=False
                    ):
    '''
    Returns:
        a arg_scopefully_connec with the parameters needed for STNet.
    '''
    # Set weight_decay for weights in conv2d and fully_connected layers.
    with slim.arg_scope([slim.conv2d, slim.fully_connected], weights_regularizer=slim.l2_regularizer(weight_decay),
                        biases_regularizer=slim.l2_regularizer(weight_decay), activation_fn=tf.nn.relu,
                        biases_initializer=tf.zeros_initializer()):

        batch_norm_params = {
            'decay': batch_norm_decay,
            'epsilon': batch_norm_epsilon
        }
        if use_batch_norm:
            normalizer_fn = slim.batch_norm
            normalizer_params = batch_norm_params
        else:
            normalizer_fn = None
            normalizer_params = {}

        # Set activation_fn and parameters for batch_norm.
        with slim.arg_scope([slim.conv2d], normalizer_fn=normalizer_fn, normalizer_params=normalizer_params,
                            padding='VALID') as scope:
            return scope




