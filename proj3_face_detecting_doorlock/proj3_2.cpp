// _1   : basic function with one-use only
// _2   : with loop for multiple-use, but somehow suddenly not working from the start

#include <opencv2/opencv.hpp>
#include <Python.h>

static const cv::String model = "res10_300x300_ssd_iter_140000_fp16.caffemodel";
static const cv::String config = "deploy.prototxt";

int main()
{
    // init py
    char file[] = "doorlock.py";
    FILE* fp;

    Py_Initialize();

    cv::VideoCapture capture(-1, cv::CAP_V4L2);
    if (!capture.isOpened()) {
        std::cerr << "camera not opened" << std::endl;
        return 1;
    }

    cv::dnn::Net net = cv::dnn::readNet(model, config);
    if (net.empty()) {
        std::cerr << "Net open failed" << std::endl;
        return 1;
    }

    cv::Mat frame;
    cv::namedWindow("DOORLOCK");
    //int detect_flag = 0;

    //while (cv::waitKey(24) != 27) {
        //int detect_flag = 0;           

        while (true) {
            int detect_flag = 0;
            capture >> frame;
            cv::Mat blob = cv::dnn::blobFromImage(frame, 1, cv::Size(300, 300), cv::Scalar(104, 177, 123)); // skin colour for Asians
            net.setInput(blob);     // 입력
            cv::Mat result = net.forward();

            cv::Mat detect(result.size[2], result.size[3], CV_32FC1, result.ptr<float>());  // result.size[2], [3] for top left and bottom right axis of face for rectangle

            for (int i = 0; i < detect.rows; ++i) {
                float CONFIDENCE = detect.at<float>(i, 2);  // column 2 = accuracy
                if (CONFIDENCE < 0.7) break;

                int x1 = cvRound(detect.at<float>(i, 3) * frame.cols);
                int y1 = cvRound(detect.at<float>(i, 4) * frame.rows);
                int x2 = cvRound(detect.at<float>(i, 5) * frame.cols);
                int y2 = cvRound(detect.at<float>(i, 6) * frame.rows);

                cv::rectangle(frame, cv::Rect(cv::Point(x1, y1), cv::Point(x2, y2)), cv::Scalar(0, 255, 0));

                cv::String label = cv::format("Face detected. Opening door");
                cv::putText(frame, label, cv::Point(10, 30), cv::FONT_HERSHEY_COMPLEX, 0.8, cv::Scalar(0, 255, 0));

                detect_flag = 1;

            }

            cv::imshow("DOORLOCK", frame);

            if (detect_flag == 1) {
                break;
                //fp = _Py_fopen(file, "r");
                //PyRun_SimpleFile(fp, file);
                //sleep(1);

            }
        }

        fp = _Py_fopen(file, "r");
        PyRun_SimpleFile(fp, file);
        //sleep(6);
    //}
   
    Py_Finalize();
    cv::destroyAllWindows();

    return 0;
}


