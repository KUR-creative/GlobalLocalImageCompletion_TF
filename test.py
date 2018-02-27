import tensorflow as tf
import numpy as np
from config import *
from network import *


drawing = False # true if mouse is pressed
ix,iy = -1,-1
color = (255,255,255)
size = 10

def erase_img(args, img):

    # mouse callback function
    def erase_rect(event,x,y,flags,param):
        global ix,iy,drawing

        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            if drawing == True:
                print 'l mouse down'
                # cv2.circle(img,(x,y),10,(255,255,255),-1)
                cv2.rectangle(img,(x-size,y-size),(x+size,y+size),color,-1)
                cv2.rectangle(mask,(x-size,y-size),(x+size,y+size),color,-1)
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing == True:
                # cv2.circle(img,(x,y),10,(255,255,255),-1)
                cv2.rectangle(img,(x-size,y-size),(x+size,y+size),color,-1)
                cv2.rectangle(mask,(x-size,y-size),(x+size,y+size),color,-1)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            print 'l mouse up'
            # cv2.circle(img,(x,y),10,(255,255,255),-1)
            cv2.rectangle(img,(x-size,y-size),(x+size,y+size),color,-1)
            cv2.rectangle(mask,(x-size,y-size),(x+size,y+size),color,-1)


    cv2.namedWindow('image')
    cv2.setMouseCallback('image',erase_rect)
    cv2.namedWindow('mask')
    cv2.setMouseCallback('mask',erase_rect)
    mask = np.zeros(img.shape)
    

    while(1):
        img_show = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        cv2.imshow('image',img_show)
        k = cv2.waitKey(1) & 0xFF
        if k != 255:
            print 'k: ', k
        if k == 13:
            break

    test_img = cv2.resize(img, (args.input_height, args.input_width))/127.5 - 1
    test_mask = cv2.resize(mask, (args.input_height, args.input_width))/255.0
    #fill mask region to 1
    test_img = (test_img * (1-test_mask)) + test_mask

    cv2.destroyAllWindows()
    return np.tile(test_img[np.newaxis,...], [args.batch_size,1,1,1]), np.tile(test_mask[np.newaxis,...], [args.batch_size,1,1,1])




def test(args, sess, model):
    #saver  
    saver = tf.train.Saver()        
    last_ckpt = tf.train.latest_checkpoint(args.checkpoints_path)
    saver.restore(sess, last_ckpt)
    ckpt_name = str(last_ckpt)
    print " ------------------------------------------------------------------------------------------------- "
    print " Loaded model file from " + ckpt_name
    
    img = cv2.imread(args.img_path)
    print '1'
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    print '2'
    orig_test = cv2.resize(img, (args.input_height, args.input_width))/127.5 - 1
    print '3'
    orig_test = np.tile(orig_test[np.newaxis,...],[args.batch_size,1,1,1])
    print '4'
    orig_test = orig_test.astype(np.float32)
    print '5'

    orig_w, orig_h = img.shape[0], img.shape[1]
    print '6'
    test_img, mask = erase_img(args, img)
    print '7'
    test_img = test_img.astype(np.float32)
    print '8'
    
    print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Testing ..."
    res_img = sess.run(model.test_res_imgs, feed_dict={model.single_orig:orig_test,
                                                       model.single_test:test_img,
                                                       model.single_mask:mask})
    print '9'

    orig = cv2.resize((orig_test[0]+1)/2, (orig_h/2, orig_w/2))
    test = cv2.resize((test_img[0]+1)/2, (orig_h/2, orig_w/2))
    #recon = cv2.resize((res_img[0]+1)/2, (orig_h/2, orig_w/2))
    recon = cv2.resize((res_img[0]+1)/2, (orig_h, orig_w))

    #res = np.hstack([orig,test,recon])
    res = np.hstack([recon])
    ''' 
    recon = cv2.resize((res_img[0]+1)/2, (1, 1))
    res = np.hstack([recon])
    '''
    res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)

    cv2.imshow("result", res)
    cv2.waitKey()

    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Done.")


def main(_):
    run_config = tf.ConfigProto()
    run_config.gpu_options.allow_growth = True
    
    with tf.Session(config=run_config) as sess:
        model = network(args)

        print 'Start Testing...'
        test(args, sess, model)

main(args)
