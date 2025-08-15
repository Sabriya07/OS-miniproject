#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <string.h>

// Disk parameters
#define RPM 7200          // Disk rotation speed (revolutions per minute)
#define SECTOR_SIZE 512   // Bytes per sector
#define TRACK_SIZE 1000   // Sectors per track
#define SEEK_RATE 0.1     // ms per cylinder seek
#define TRANSFER_RATE 125 // 1MB/s (1000000 bytes/sec = 125 sectors/ms)

// Global variables
int disk_size = 200;
int direction = 1;  // 1 for right, 0 for left
int i, j;

// Function prototypes
int fcfs(int requests[], int n, int head, int* sequence);
int sstf(int requests[], int n, int head, int* sequence);
int scan(int requests[], int n, int head, int* sequence);
int look(int requests[], int n, int head, int* sequence);
int cscan(int requests[], int n, int head, int* sequence,int direction);
int clook(int requests[], int n, int head, int* sequence,int direction);
void sort_array(int arr[], int n);

// Helper function to sort array
void sort_array(int arr[], int n) {
    for (i = 0; i < n-1; i++) {
        for (j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                int temp = arr[j];
                arr[j] = arr[j+1];
                arr[j+1] = temp;
            }
        }
    }
}

// FCFS implementation
int fcfs(int requests[], int n, int head, int* sequence) {
    int total_movement = 0;
    sequence[0] = head;
    for (i = 0; i < n; i++) {
        total_movement += abs(head - requests[i]);
        head = requests[i];
        sequence[i+1] = head;
    }
    return total_movement;
}

// SSTF implementation
int sstf(int requests[], int n, int head, int* sequence) {
    int visited[n];
    memset(visited, 0, sizeof(visited));
    int total_movement = 0;
    sequence[0] = head;
    
    for (i = 0; i < n; i++) {
        int min_dist = INT_MAX;
        int min_index = -1;
        
        for (j = 0; j < n; j++) {
            if (!visited[j] && abs(head - requests[j]) < min_dist) {
                min_dist = abs(head - requests[j]);
                min_index = j;
            }
        }
        
        if (min_index == -1) break;
        
        visited[min_index] = 1;
        total_movement += min_dist;
        head = requests[min_index];
        sequence[i+1] = head;
    }
    
    return total_movement;
}

// SCAN (Elevator) implementation
int scan(int requests[], int n, int head, int* sequence) {
    int sorted[n];
    memcpy(sorted, requests, n * sizeof(int));
    sort_array(sorted, n);
    
    int total_movement = 0;
    int seq_index = 0;
    sequence[seq_index++] = head;
    
    if (direction == 1) { // Moving right
        for (i = 0; i < n; i++) {
            if (sorted[i] >= head) {
                total_movement += sorted[i] - head;
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
        total_movement += (disk_size - 1 - head);
        head = disk_size - 1;
        sequence[seq_index++] = head;
        
        for (i = n-1; i >= 0; i--) {
            if (sorted[i] < head) {
                total_movement += head - sorted[i];
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
    } else { // Moving left
        for (i = n-1; i >= 0; i--) {
            if (sorted[i] <= head) {
                total_movement += head - sorted[i];
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
        total_movement += head;
        head = 0;
        sequence[seq_index++] = head;
        
        for (i = 0; i < n; i++) {
            if (sorted[i] > head) {
                total_movement += sorted[i] - head;
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
    }
    
    return total_movement;
}

// LOOK implementation
int look(int requests[], int n, int head, int* sequence) {
    int sorted[n];
    memcpy(sorted, requests, n * sizeof(int));
    sort_array(sorted, n);
    
    int total_movement = 0;
    int seq_index = 0;
    sequence[seq_index++] = head;
    
    if (direction == 1) { // Moving right
        for (i = 0; i < n; i++) {
            if (sorted[i] >= head) {
                total_movement += sorted[i] - head;
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
        
        for (i = n-1; i >= 0; i--) {
            if (sorted[i] < head) {
                total_movement += head - sorted[i];
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
    } else { // Moving left
        for (i = n-1; i >= 0; i--) {
            if (sorted[i] <= head) {
                total_movement += head - sorted[i];
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
        
        for (i = 0; i < n; i++) {
            if (sorted[i] > head) {
                total_movement += sorted[i] - head;
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
    }
    
    return total_movement;
}

int cscan(int requests[], int n, int head, int* sequence, int direction) {
    int sorted[n];
    memcpy(sorted, requests, n * sizeof(int));
    sort_array(sorted, n);

    int total_movement = 0;
    int seq_index = 0;
    int initial_head = head;
    sequence[seq_index++] = head;

    if (direction == 1) { // Moving right
        // Service requests to the right
        for ( i = 0; i < n; i++) {
            if (sorted[i] >= initial_head) {
                total_movement += abs(sorted[i] - head);
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }

        // Move to end of disk if needed
        if (head != disk_size - 1) {
            total_movement += (disk_size - 1 - head);
            head = disk_size - 1;
            sequence[seq_index++] = head;
        }

        // Jump to beginning
        total_movement += (disk_size - 1);
        head = 0;
        sequence[seq_index++] = head;

        // Service remaining requests (left of initial head)
        for ( i = 0; i < n; i++) {
            if (sorted[i] < initial_head) {
                total_movement += abs(sorted[i] - head);
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }

    } else { // Moving left
        // Service requests to the left
        for ( i = n-1; i >= 0; i--) {
            if (sorted[i] <= initial_head) {
                total_movement += abs(head - sorted[i]);
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }

        // Move to start of disk if needed
        if (head != 0) {
            total_movement += head;
            head = 0;
            sequence[seq_index++] = head;
        }

        // Jump to end
        total_movement += (disk_size - 1);
        head = disk_size - 1;
        sequence[seq_index++] = head;

        // Service remaining requests (right of initial head)
        for ( i = n-1; i >= 0; i--) {
            if (sorted[i] > initial_head) {
                total_movement += abs(head - sorted[i]);
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
    }
    return total_movement;
}

int clook(int requests[], int n, int head, int* sequence, int direction) {
    int sorted[n];
    memcpy(sorted, requests, n * sizeof(int));
    sort_array(sorted, n);
    
    int total_movement = 0;
    int seq_index = 0;
    sequence[seq_index++] = head;
    
    if (direction == 1) { // Moving right
        for (i = 0; i < n; i++) {
            if (sorted[i] >= head) {
                total_movement += abs(head - sorted[i]);
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
        
        if (sorted[0] < head) { // If wrap-around needed
            total_movement += abs(head - sorted[0]);
            head = sorted[0];
            sequence[seq_index++] = head;
            
            for (i = 1; i < n; i++) {
                if (sorted[i] > head) {
                    total_movement += abs(sorted[i] - head);
                    head = sorted[i];
                    sequence[seq_index++] = head;
                }
            }
        }
        
    } else { // Moving left
        for (i = n-1; i >= 0; i--) {
            if (sorted[i] <= head) {
                total_movement += abs(head - sorted[i]);
                head = sorted[i];
                sequence[seq_index++] = head;
            }
        }
        
        if (sorted[n-1] > head) { // If wrap-around needed
            total_movement += abs(head - sorted[n-1]);
            head = sorted[n-1];
            sequence[seq_index++] = head;
            
            for (i = n-2; i >= 0; i--) {
                if (sorted[i] < head) {
                    total_movement += abs(head - sorted[i]);
                    head = sorted[i];
                    sequence[seq_index++] = head;
                }
            }
        }
    }
    
    return total_movement;
}


// Main function
int main(int argc, char *argv[]) {
    if (argc < 6) {
        printf("Usage: %s <algorithm> <head> <disk_size> <direction> <requests...>\n", argv[0]);
        return 1;
    }

    char *algorithm = argv[1];
    int head = atoi(argv[2]);
    disk_size = atoi(argv[3]);
    direction = atoi(argv[4]);

    int n = argc - 5;
    int requests[n];
    for (i = 0; i < n; i++) {
        requests[i] = atoi(argv[i+5]);
    }

    int sequence[n + 100];  // Enough space for movements
    memset(sequence, -1, sizeof(sequence));  // Initialize with -1
    
    int total_movement = 0;
    float seek_time, rotational_latency, transfer_time, total_time;

    if (strcmp(algorithm, "FCFS") == 0) {
        total_movement = fcfs(requests, n, head, sequence);
    } else if (strcmp(algorithm, "SSTF") == 0) {
        total_movement = sstf(requests, n, head, sequence);
    } else if (strcmp(algorithm, "SCAN") == 0) {
        total_movement = scan(requests, n, head, sequence);
    } else if (strcmp(algorithm, "LOOK") == 0) {
        total_movement = look(requests, n, head, sequence);
    } else if (strcmp(algorithm, "C-SCAN") == 0) {
    total_movement = cscan(requests, n, head, sequence, direction);
	} else if (strcmp(algorithm, "C-LOOK") == 0) {
    	total_movement = clook(requests, n, head, sequence, direction);
	}
 else {
        printf("Unknown algorithm: %s\n", algorithm);
        return 1;
    }

    // Calculate time components
    seek_time = total_movement * SEEK_RATE;
    rotational_latency = (60.0 * 1000) / (RPM * 2);  // Average rotational latency in ms
    transfer_time = n * SECTOR_SIZE / (TRANSFER_RATE * 1000.0);  // Transfer time in ms
    total_time = seek_time + rotational_latency + transfer_time;

    // Print output in the required format
    printf("%d|%.2f|%.2f|%.2f|%.2f|", total_movement, seek_time, 
           rotational_latency, transfer_time, total_time);
    
    // Print sequence (comma-separated without spaces)
    int seq_length = 0;
    while (sequence[seq_length] != -1 && seq_length < n + 100) {
        if (seq_length > 0) printf(",");
        printf("%d", sequence[seq_length]);
        seq_length++;
    }
    printf("\n");

    return 0;
}
