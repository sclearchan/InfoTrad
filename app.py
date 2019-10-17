import library.ea as ea
import library.yz as yz
import library.gan as gan


if __name__ == "__main__":
  BUYDATA = [350,250,500,552,163,345,847,923,123,349]
  SELLDATA = [382,500,463,550,200,323,456,342,578,455]
  data = []

  for idx, val in enumerate(BUYDATA):
    data.append([val,SELLDATA[idx]])

  instance = ea.EAClass();
  # instance = yz.YZClass();
  # instance = gan.GANClass();
  res = instance.run(data, "LK");
  print(res)

  # print('data sum: ',np.mean(BUYDATA)+np.mean(SELLDATA))
  # print('param sum: ', res.x[0]*res.x[2] + res.x[3] + res.x[4])
