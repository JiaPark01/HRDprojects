// _1   : basic function with one-use only
// _2   : with loop for multiple-use, but somehow suddenly not working from the start
// --> rename to doorlock_client.cpp
// _1   : start over with socket prg, run once
// _2   : keep the prg alive
// _3   : capture image when door opened
// _4   : **fix image name bug**
// _5   : change month to int
// _6   : tried to keep ' and $ for further use when they are needed

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
#include <vector>
// new
#include <chrono>   // for timestamp when exporting image to file
#include <ctime>    // "

static void* send_message(void*);
//static void* receive_message(void*);
static void error_handling(const char*);
static int detect_face();
// new
//static void rename(std::string& str);
static void replaceAll(std::string& str, const std::string& from, const std::string& to);  // replace all substring within the given string
static std::vector<std::string> split(std::string str, std::string delim);  // split a string with given delimiter and return them in a vector
static std::string monthToInt(std::string month);   // convert string month to a string of an integer ("May" --> "05")

static const cv::String model = "res10_300x300_ssd_iter_140000_fp16.caffemodel";
static const cv::String config = "deploy.prototxt";
char message[BUFSIZ] = {'\0',};
// new
std::vector<std::string>months = { "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" };
                                // for monthToInt func.

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
            // new
            detect_flag = true; // to open the door only when face is detected
        }
        
        cv::imshow("DOORLOCK", frame);
        if (cv::waitKey(24) == 27) {                                // if esc is pressed
            cv::destroyAllWindows();                                // close the camera and shut down
            std::cout << "Bye" << std::endl;
            return NULL;
        }

        // new
        if (detect_flag == true) {                                  // if face detected, then send message to python to open the door
            int sock = *((int*)args);
            char message[BUFSIZ] = {'\0', };
            sprintf(message, "%s", "open");                         // send "open"
            write(sock, message, strlen(message));
            std::cout << "open" << std::endl;
            // new
            std::time_t now = std::chrono::system_clock::to_time_t(std::chrono::system_clock::now());   // timestamp of current time in integer
            std::string date_time = std::ctime(&now);               // convert integer to date and time format
            
            replaceAll(date_time, ":", "-");                        // cannot use ':' in a file name, so replace it with '-'
            replaceAll(date_time, "\n", "");                        // made problems in saving file with strange format ('$'\n'), so remove them

            std::string delim = " ";                                // set delimiter as space for split
            std::vector<std::string> tokens = split(date_time, delim);  // save splitted date_time into tokens vector

            date_time = tokens[4];                                  // reset date_time var with the year token
            std::string month = monthToInt(tokens[1]);              // convert month to number ("May" --> "5")
            date_time.insert(date_time.size(), "_" + month);        // append the month to year with "_"
            date_time.insert(date_time.size(), "_" + tokens[2]);    // append date
            date_time.insert(date_time.size(), "_" + tokens[0]);    // apend day of week
            date_time.insert(date_time.size(), "_" + tokens[3]);    // append time
            date_time.insert(date_time.size(), ".png");             // append .png

            cv::imwrite(date_time, frame);                          // export camera with face with the title of current date and time

            sleep(2);                                               // pause screen for two seconds for convenience (how the pic was taken)
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

// new
void replaceAll(std::string& str, const std::string& from, const std::string& to)
{
    if(from.empty())                        // exit func if nothing for prev string is empty
        return;
    size_t pos = 0;                         // set starting position of the string
    while((pos = str.find(from, pos)) != std::string::npos) {   // begin finding 'from' until end of string
        str.replace(pos, from.length(), to);// replace the string
        pos += to.length();                 // skip the length of 'to' in case 'to' contains 'from' ("x" with "yx")
    }
}

std::vector<std::string> split(std::string str, std::string delim)
{
    std::string s = str;                    // make copy of string to modify
    size_t pos = 0;                         // set starting position of the string
    std::string token;                      // for each word in string after split
    std::vector<std::string> tokens;        // vector to contain the tokens

    while ((pos = s.find(delim)) != std::string::npos) {    // begin finding " " until end of string
        token = s.substr(0, pos);           // take substring from beginning until " "
        tokens.push_back(token);            // add the token to the vector
        s.erase(0, pos + delim.length());   // erase the string from beginning to the length of substring and delimiter
    }
    tokens.push_back(s);                    // insert the final token since there is no delimiter at the end

    return tokens;                          // return the vector
}

std::string monthToInt(std::string month)
{
    for (int i = 0; i < 12; ++i) {          // loop 12 times to find the month
        if (month == months[i]) {           // if the given month matches the one in the months vector the month is found
            if (i + 1 >= 10) return std::to_string(i+1);    // if i+1 is greater than 10, just return the number+1
            else return "0" + std::to_string(i+1);          // else, add 0 at the front
        }
    }
    return 0;
}