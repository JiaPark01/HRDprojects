// _1   : basic function with one-use only
// _2   : with loop for multiple-use, but somehow suddenly not working from the start
// --> rename to doorlock_client.cpp
// _1   : start over with socket prg, run once
// _2   : keep the prg alive

#include <opencv2/opencv.hpp>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdbool.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <pthread.h>
#include <sys/types.h>
#include <assert.h>

static int detect_face();
static void* send_message(void*);
//static void* receive_message(void*);
static void error_handling(const char*);

static const cv::String model = "res10_300x300_ssd_iter_140000_fp16.caffemodel";
static const cv::String config = "deploy.prototxt";
char message[BUFSIZ] = {'\0',};

int main(int argc, const char** argv)
{
    int sock = 0;
    struct sockaddr_in serv_addr;
    pthread_t send_thread;
    pthread_t receive_thread;

    void* thread_return = NULL;

    if(argc != 3) {
        error_handling("./DOORLOCK_CLIENT 127.0.0.1 9999");
    }

    // 1. socket()
    if((sock = socket(PF_INET, SOCK_STREAM, 0)) == -1) {
        error_handling("socket() error");
    }
    memset(&serv_addr, 0, sizeof serv_addr);

    serv_addr.sin_family = AF_INET;
    serv_addr.sin_addr.s_addr = inet_addr(argv[1]);
    serv_addr.sin_port = htons(atoi(argv[2]));

    // 2. connect()
    if(connect(sock, (const struct sockaddr*)&serv_addr, sizeof serv_addr) == -1) {
        error_handling("connect() error");
    }

    pthread_create(&send_thread, NULL, send_message, (void*)&sock);
    //pthread_create(&receive_thread, NULL, receive_message, (void*)&sock);
    pthread_join(send_thread, &thread_return);
    //pthread_join(receive_thread, &thread_return);

    return 0;
}


void* send_message(void* args)

{
    cv::VideoCapture capture(-1, cv::CAP_V4L2);
    if (!capture.isOpened()) {
        std::cerr << "camera not opened" << std::endl;
        return NULL;
    }

    cv::dnn::Net net = cv::dnn::readNet(model, config);
    if (net.empty()) {
        std::cerr << "Net open failed" << std::endl;
        return NULL;
    }

    cv::Mat frame;
    cv::namedWindow("DOORLOCK");

    while (true) {
        int detect_flag = false;

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

            cv::String label = cv::format("Face detected. Opening door...");
            cv::putText(frame, label, cv::Point(10, 30), cv::FONT_HERSHEY_COMPLEX, 0.8, cv::Scalar(0, 255, 0));

            detect_flag = true;
        }
        
        cv::imshow("DOORLOCK", frame);
        if (cv::waitKey(24) == 27) {
            cv::destroyAllWindows();
            std::cout << "Bye" << std::endl;
            return NULL;
        }

        if (detect_flag == true) {
            int sock = *((int*)args);
            char message[BUFSIZ] = {'\0', };
            sprintf(message, "%s", "open");
            write(sock, message, strlen(message));
            std::cout << "open" << std::endl;
            
            sleep(2);
        }
    }
    return NULL;
}

void error_handling(const char* _message)
{
    fputs(_message, stdout);
    fputs("\r\n", stdout);
    exit(1);
}